#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ContactDetail, ServiceDeliveryPointStatusType, ServiceDeliveryPointStatus, ServiceDeliveryPoint, Facility, District
from datetime import timedelta, datetime, time
from utils import *
from dateutil.relativedelta import *
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from dateutil.rrule import *
from dateutil.parser import *
from django.db.models import Count, Max

######################
# Callback Functions #
######################

TEST_MODE = False
#  Next steps: 
#  1) collapse into a single callback method
#  2) change to a config dict
#  3) move to database settings

def _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    default_query=ServiceDeliveryPoint.objects.all(),
                    bysetpos=-1,
                    message_kwargs={}):
    
    now = datetime.now()
    additional_reminders_to_send_count = len(additional_reminders_to_send)
    sdp_status_type = ServiceDeliveryPointStatusType.objects.filter(short_name=reminder_name)[0:1].get()
    
    #create a date rule (for business day logic) - last weekday prior to monthday, 31 means the end of any month
    if monthday:
        rr1 = rrule(MONTHLY, 
                    interval=1, 
                    dtstart=now + relativedelta(months=-2), 
                    until=  now + relativedelta(months=+2), 
                    byweekday=(MO,TU,WE,TH,FR), 
                    byhour=byhour, 
                    bysetpos=bysetpos,
                    byminute=byminute,
                    bymonthday=(monthday-2, monthday-1, monthday))
    else:
        rr1 = rrule(MONTHLY, 
                    interval=1, 
                    dtstart=now + relativedelta(months=-2), 
                    until=  now + relativedelta(months=+2), 
                    byweekday=(MO,TU,WE,TH,FR), 
                    byhour=byhour, 
                    bysetpos=bysetpos,
                    byminute=byminute)
        
    start_time = rr1.before(now)
    end_time = rr1.after(now)
    

    # query for sdps with no reminders sent 
    q_no_reminders = default_query.exclude(servicedeliverypointstatus__status_date__range=(start_time, end_time),
                                           servicedeliverypointstatus__status_type=sdp_status_type) 
    
    # query for sdps with reminders sent: annotate to count the number of reminders sent
    q_reminders = default_query.filter(servicedeliverypointstatus__status_date__range=(start_time, end_time),
                                        servicedeliverypointstatus__status_type=sdp_status_type) \
                                        .annotate(last_status_date=Max('servicedeliverypointstatus__status_date'),
                                                  status_count=Count('servicedeliverypointstatus'))
    q_reminders = q_reminders.filter(status_count__lt=additional_reminders_to_send_count)
            
    #logging.debug("No reminder sent query: %s, count %d" % (q_no_reminders, len(q_no_reminders)))
    #logging.debug("Reminders already sent query: %s, count %d" % (q_reminders, len(q_reminders)))
    logging.debug("Sending Reminders for %s:" % reminder_name)
    logging.debug("  Reminder start window: %s" % start_time)
    logging.debug("  Reminder end window: %s" % end_time)
    logging.debug("  Sending initial reminders:")
    for sdp in q_no_reminders:
        contact_details_to_remind = sdp.contacts('primary')
        sent = False
        for contact_detail in contact_details_to_remind:
            default_connection = contact_detail.default_connection
            if default_connection:
                m = get_message(contact_detail, reminder_name, **message_kwargs)
                if m:
                    logging.debug("    sdp %s (delivery group: %s) hasn't yet received their %s reminder, contact detail %s" % (sdp, 
                                                                                                                            sdp.delivery_group, 
                                                                                                                            reminder_name, 
                                                                                                                            contact_detail))
                    m.send()
                    sent = True
        if sent:
            ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, 
                                            status_type=sdp_status_type, 
                                            status_date=datetime.now())
            ns.save()
    
    logging.debug("  Sending followup reminders:")
    for sdp in q_reminders:
        next_reminder = additional_reminders_to_send[sdp.status_count]
        #TODO: Do we want a check to see whether the reminder has gone out already today (if the server was down, or some other reason?)
#        if sdp.last_status_date > start_time:
#            start_time = sdp.last_status_date
        rr2 = rrule(DAILY, 
            dtstart=start_time, 
            count=next_reminder['additional_business_days'],
            byhour=next_reminder['hour'],
            byminute=next_reminder['minute'],
            bysecond=0,
            byweekday=(MO,TU,WE,TH,FR))            
        next_reminder_date = list(rr2).pop()
        
        logging.debug("    Last status date: %s" % sdp.last_status_date)
        if datetime.now() > next_reminder_date:
            contact_details_to_remind = sdp.contacts('primary')
            sent = False
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    logging.debug("      %s %s" % (contact_detail, default_connection))
                    m = get_message(contact_detail, reminder_name, **message_kwargs)
                    if m:
                        m.send()
                        sent = True           
            if sent:
                ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, 
                                                status_type=sdp_status_type, 
                                                status_date=datetime.now())
                ns.save()     
                logging.debug("    SDP %s (delivery group %s) has already received %d %s reminders and is past reminder date %s for %s, sending reminder to the following contacts" % ( \
                         sdp, 
                         sdp.delivery_group, 
                         sdp.status_count,
                         reminder_name,
                         next_reminder_date, 
                         reminder_name))
        else:
                logging.debug("    SDP %s (delivery group %s) has already received %d %s reminders, next one is set for %s" % ( \
                             sdp, 
                             sdp.delivery_group, 
                             sdp.status_count,
                             reminder_name,
                             next_reminder_date))

    logging.info("%s (%s) sent to all PRIMARY contacts" % (sdp_status_type.name, sdp_status_type.short_name))

def district_delinquent_deliveries_summary(router):
    reminder_name = "alert_delinquent_delivery_sent_district"

    # 7 days prior to the last day of the month - we leave off monthday because rrule barfs on setpos/monthday conflicts
    bysetpos=     -7
    # 2pm
    byhour =      8 
    byminute =    0

    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":1, "hour": 8, "minute": 0},
                                    {"additional_business_days":1, "hour": 14, "minute": 0}]
    
    #send them out
    _send_reminders(router,
                    reminder_name,
                    None, #leave out monthday
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    District.objects.all(),
                    bysetpos=bysetpos)

def facility_soh_reminder(router):
    #Reminder window: the last weekday of the month at 2pm to the last weekday of the following month at 2pm 
    monthday=31
    
    reminder_name = "soh_reminder_sent_facility"
    
    # 2pm
    byhour =      14 
    byminute =    0
    
    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":1, "hour": 8, "minute": 15},
                                    {"additional_business_days":5, "hour": 8, "minute": 15}]
    
    #send them out
    _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    Facility.objects.all())

def facility_randr_reminder(router):
    reminder_name = "r_and_r_reminder_sent_facility"
    
    # 5th business day of the month
    monthday =    5
    
    # 2pm
    byhour =      14 
    byminute =    0
    
    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":5, "hour": 8, "minute": 0},
                                    {"additional_business_days":7, "hour": 8, "minute": 0}]
    #send them out
    _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    Facility.objects.filter(delivery_group__name=current_submitting_group()))
        
def district_randr_reminder(router):
    reminder_name = "r_and_r_reminder_sent_district"

    #The last weekday of the month prior to the 13th
    monthday =    13
    
    # 2pm
    byhour =      8 
    byminute =    0

    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":2, "hour": 8, "minute": 0},
                                    {"additional_business_days":3, "hour": 14, "minute": 0}]
    #send them out
    _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    District.objects.all())
        
def facility_delivery_reminder(router):
    reminder_name = "delivery_received_reminder_sent_facility"

    #The last weekday of the month prior to the 15th
    monthday =    15
    
    # 2pm
    byhour =      14 
    byminute =    0

    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":2, "hour": 8, "minute": 0},
                                    {"additional_business_days":3, "hour": 14, "minute": 0},
                                    {"additional_business_days":5, "hour": 14, "minute": 0}]
    #send them out
    _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,
                    additional_reminders_to_send,
                    Facility.objects.filter(delivery_group__name=current_delivering_group()))
    
def district_delivery_reminder(router):
    # TODO: This should skip districts that don't have any deliveries expected - for example, if there are no facilities in Group C then there won't be deliveries expected in March 
    reminder_name = "delivery_received_reminder_sent_district"

    #The last weekday of the month prior to the 13th at 2pm
    monthday =    13
    byhour =      14 
    byminute =    0

    # additional reminders
    additional_reminders_to_send = [{"additional_business_days":7, "hour": 14, "minute": 0},
                                    {"additional_business_days":15, "hour": 14, "minute": 0}]
    #send them out
    _send_reminders(router,
                    reminder_name,
                    monthday,
                    byhour,
                    byminute,                    
                    additional_reminders_to_send,
                    District.objects.all())

#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ContactDetail, ServiceDeliveryPointStatusType, ServiceDeliveryPointStatus, ServiceDeliveryPoint
from datetime import timedelta, datetime
from utils import *
from dateutil.relativedelta import *
from django.db.models import Q

######################
# Callback Functions #
######################

TEST_MODE = True

def is_weekend():  
    return False
    if datetime.now().date().weekday() in [5,6]:
        return True
    else:
        return False

def district_delinquent_deliveries_summary(router):
    now = datetime.now()
    # run seven days before the last day of the current month
    if TEST_MODE or (now.day == now + relativedelta(day=31,days=-7)):
        contact_details_to_remind = ContactDetail.objects.filter(primary=True,
                                                                 service_delivery_point__service_delivery_point_type__name="DISTRICT")
        for contact_detail in contact_details_to_remind:
            default_connection = contact_detail.default_connection
            if default_connection:
                service_delivery_point = contact_detail.service_delivery_point
                if service_delivery_point.child_sdps_not_received_delivery_this_month() + service_delivery_point.child_sdps_not_responded_delivery_this_month() > 0:
                    m = OutgoingMessage(default_connection, 
                                        "Facility deliveries for group %s (out of %d): %d haven't responded and %d have reported not receiving. See ilsgateway.com" % 
                                        (current_delivering_group(), 
                                         service_delivery_point.child_sdps().filter(delivery_group__name=current_delivering_group()).count(), 
                                         service_delivery_point.child_sdps_not_responded_delivery_this_month(), 
                                         service_delivery_point.child_sdps_not_received_delivery_this_month()))
                    m.send()         
                    
        logging.info("District delivery reminder sent to all PRIMARY district contacts")

def facility_soh_reminder(router):
    now = datetime.now()
    # last day of the month and check for the first 4 days of the next month
    if TEST_MODE or now.day == (now + relativedelta(day=31)).day or now.day < 5:
        #TODO: This query needs to be pared down
        contact_details_to_remind = ContactDetail.objects.filter(primary=True,
                                                                 service_delivery_point__service_delivery_point_type__name="FACILITY")
        for contact_detail in contact_details_to_remind:
            if now.day < 5:
                #last day of last month
                date_check = now + relativedelta(day=31, months=-1)
            else:
                #last day of this month (today)
                date_check = now + relativedelta(day=31)
                
            if not contact_detail.service_delivery_point.received_reminder_after("soh_reminder_sent_facility", date_check):
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, "Please send in your stock on hand information in the format \"soh inj 200 con 344 imp 20\"")
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="soh_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
            elif not contact_detail.service_delivery_point.received_reminder_after("soh_reminder_sent_facility", now + relativedelta(days=-3)):
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, "Please send in your stock on hand information in the format \"soh inj 200 con 344 imp 20\"")
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="soh_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
    
        logging.info("Stock on hand reminder message sent to all PRIMARY facility in-charges")

def facility_randr_reminder(router):
    # Send a reminder on the first business day after the 5th
    if TEST_MODE or (not is_weekend() and datetime.now().day >= 5):
        all_current_submitting_contact_details = ContactDetail.objects.filter(service_delivery_point__delivery_group__name=current_submitting_group(), primary=True)
        for contact_detail in all_current_submitting_contact_details:
            if not contact_detail.service_delivery_point.received_reminder_after("r_and_r_reminder_sent_facility", beginning_of_month(datetime.now().month)):
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, "Have you sent in your R&R form yet for this quarter?  Please reply \"yes\" or \"not sent\"")
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
    
        logging.info("R&R reminder message sent to all PRIMARY facility in-charges")
        
def district_randr_reminder(router):
    #Send a reminder the first business day after the 15th
    if TEST_MODE or (not is_weekend() and datetime.now().day >= 15): 
        district_contact_details = ContactDetail.objects.filter(role__name__exact='DMO', primary=True)
        for contact_detail in district_contact_details:
            if not contact_detail.service_delivery_point.received_reminder_after("r_and_r_reminder_sent_district", beginning_of_month(datetime.now().month)):
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, "It's time to submit group %s.  How many R&R forms have you submitted to MSD so far?  Reply with \"submitted 20 a 10 b 2 c\"." % current_submitting_group() )
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_district")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
    
        logging.info("R&R reminder message sent to all PRIMARY district in-charges")        
        
def facility_delivery_reminder(router):
    # Reminder on the 15th regardless of weekend
    if TEST_MODE or (datetime.now().day >= 15): 
        all_current_delivery_facilities = ServiceDeliveryPoint.objects.filter(delivery_group__name=current_delivering_group())
        for facility in all_current_delivery_facilities:
            if not facility.received_reminder_after("delivery_received_reminder_sent_facility", beginning_of_month(datetime.now().month)):
                for fic_cd in facility.primary_contacts():
                    c = fic_cd.default_connection
                    if c:
                        m = OutgoingMessage(c, "%s: Did you receive your delivery yet?  Please reply \"delivered\" or \"not delivered\"" % (fic_cd.name))
                        m.send() 
                        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_reminder_sent_facility")[0:1].get()
                        ns = ServiceDeliveryPointStatus(service_delivery_point=fic_cd.service_delivery_point, status_type=st, status_date=datetime.now())
                        ns.save()
                
        logging.info("Delivery reminder message sent to all PRIMARY facility in-charges")                  
        
def district_delivery_reminder(router):
    # Reminder on the first business day after the 15th
    if TEST_MODE or (not is_weekend() and datetime.now().day >= 15):
        # TODO: This should skip districts that don't have any deliveries expected - for example, if there are no facilities in Group C then there won't be deliveries expected in March 
        all_districts = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name="DISTRICT")
        for district in all_districts:
            if not district.received_reminder_after("delivery_received_reminder_sent_district", beginning_of_month(datetime.now().month)):
                for contact_detail in district.primary_contacts():
                    default_connection = contact_detail.default_connection
                    if default_connection:
                        m = OutgoingMessage(default_connection, "%s: Did you receive your delivery yet?  Please reply \"delivered\" or \"not delivered\"" % (contact_detail.name))
                        m.send() 
                        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_reminder_sent_district")[0:1].get()
                        ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                        ns.save()
                
        logging.info("Delivery reminder message sent to all PRIMARY district contacts")                          
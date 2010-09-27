#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ContactDetail, ServiceDeliveryPointStatusType, ServiceDeliveryPointStatus, ServiceDeliveryPoint
from datetime import timedelta, datetime
from utils import end_of_month, beginning_of_month

######################
# Callback Functions #
######################

def is_weekend():  
    return False
    if datetime.now().date().weekday() in [5,6]:
        return True
    else:
        return False

def current_submitting_group():
    months = {1:"A", 2:"B", 3:"C", 4:"A", 5:"B", 6:"C", 7:"A", 8:"B", 9:"C", 10:"A", 11:"B", 12:"C",}    
    return months[datetime.now().date().month]

def current_delivering_group():
    months = {3:"A", 4:"B", 5:"C", 6:"A", 7:"B", 8:"C", 9:"A", 10:"B", 11:"C", 12:"A", 1:"B", 2:"C",}    
    return months[datetime.now().date().month]
    

def facility_randr_reminder(router):
    # Send a reminder on the first business day after the 15th
    if not is_weekend() and datetime.now().day >= 15:
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
    #Send a reminder the 21st of the submission month
    if not is_weekend() and datetime.now().day >= 21: 
        district_contact_details = ContactDetail.objects.filter(role__name__exact='DMO', primary=True)
        for contact_detail in district_contact_details:
            if not contact_detail.service_delivery_point.received_reminder_after("r_and_r_reminder_sent_district", beginning_of_month(datetime.now().month)):
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, "It's time to submit group %s R&R forms to MSD." % current_submitting_group() )
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_district")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
    
        logging.info("R&R reminder message sent to all PRIMARY district in-charges")        
        
def facility_delivery_reminder(router):
    if not is_weekend(): 
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
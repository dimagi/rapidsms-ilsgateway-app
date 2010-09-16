#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ContactDetail, ServiceDeliveryPointStatusType, ServiceDeliveryPointStatus
import datetime

######################
# Callback Functions #
######################

def facility_randr_reminder(router):
    facility_in_charge_contact_details = ContactDetail.objects.filter(role__name__exact='Facility in-charge')
    facility_in_charge_contact_details = facility_in_charge_contact_details.filter(primary=True)
    for fic_cd in facility_in_charge_contact_details:
        c = fic_cd.default_connection
        if c:
            m = OutgoingMessage(c, "%s: Please send in your R&R form by Sep 15 2010 and reply \"submitted\"" % (fic_cd.name))
            m.send() 
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_facility")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=fic_cd.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
            ns.save()

    logging.info("R&R reminder message sent to all PRIMARY facility in-charges")
        
def district_randr_reminder(router):
    district_contact_details = ContactDetail.objects.filter(role__name__exact='DMO')
    district_contact_details = district_contact_details.filter(primary=True)
    for dmo_cd in district_contact_details:
        c = dmo_cd.default_connection
        if c:
            m = OutgoingMessage(c, "%s: Please send in your R&R forms by Sep 15 2010 and reply \"submitted\"" % (dmo_cd.name))
            m.send() 
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_district")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=dmo_cd.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
            ns.save()
    
    logging.info("R&R reminder message sent to all PRIMARY district in-charges")        
        
def facility_delivery_reminder(router):
    facility_in_charge_contact_details = ContactDetail.objects.filter(role__name__exact='Facility in-charge')
    facility_in_charge_contact_details = facility_in_charge_contact_details.filter(primary=True)
    for fic_cd in facility_in_charge_contact_details:
        c = fic_cd.default_connection
        if c:
            m = OutgoingMessage(c, "%s: Did you receive your delivery yet?  Please reply \"dlvd\"" % (fic_cd.name))
            m.send() 
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_reminder_sent_facility")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=fic_cd.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
            ns.save()
    
    logging.info("Delivery reminder message sent to all PRIMARY facility in-charges")                  
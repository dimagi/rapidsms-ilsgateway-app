#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ContactDetail, NodeStatusType, NodeStatus
import datetime

######################
# Callback Functions #
######################

def facility_randr_reminder(router):
    facility_in_charge_contact_details = ContactDetail.objects.filter(role__name__exact='Facility in-charge')
    facility_in_charge_contact_details = facility_in_charge_contact_details.filter(primary=True)
    for fic_cd in facility_in_charge_contact_details:
        c = fic_cd.connection()
        m = OutgoingMessage(c, "%s: Please send in your R&R form by Sep 1 2010 and reply \"submitted\"" % (fic_cd.contact.name))
        m.send() 
        st = NodeStatusType.objects.filter(short_name="r_and_r_reminder_sent")[0:1].get()
        ns = NodeStatus(node=fic_cd.node, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        logging.info(fic_cd.node.name)
        logging.info("R&R reminder message sent to all PRIMARY facility in-charges")
        
def facility_delivery_reminder(router):
    facility_in_charge_contact_details = ContactDetail.objects.filter(role__name__exact='Facility in-charge')
    facility_in_charge_contact_details = facility_in_charge_contact_details.filter(primary=True)
    for fic_cd in facility_in_charge_contact_details:
        c = fic_cd.connection()
        m = OutgoingMessage(c, "%s: Did you receive your delivery yet?  Please reply \"dlvd\"" % (fic_cd.contact.name))
        m.send() 
        st = NodeStatusType.objects.filter(short_name="delivery_received_reminder_sent")[0:1].get()
        ns = NodeStatus(node=fic_cd.node, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        logging.info(fic_cd.node.name)
        logging.info("Delivery reminder message sent to all PRIMARY facility in-charges")                  
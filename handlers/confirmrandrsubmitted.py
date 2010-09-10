#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.pattern import PatternHandler
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ContactDetail
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
import datetime

class ConfirmRandRSubmitted(PatternHandler):
    #todo: this should move up to the app level probably
    pattern = r'^subm.*$'
    def handle(self):
        service_delivery_point=self.msg.contact.contactdetail.service_delivery_point
        if service_delivery_point.service_delivery_point_type.name == "District":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_submitted_district_to_msd")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.datetime.now())
            ns.save()
            self.respond('Thank you %s for submitting your R&R forms for district %s' % (self.msg.contact.name,self.msg.contact.contactdetail.service_delivery_point.name))
            contacts_to_notify = ContactDetail.objects.filter(service_delivery_point__parent_service_delivery_point__id=9, primary=True, service_delivery_point__delivery_group__name='A')
            for contact in contacts_to_notify:
                m = OutgoingMessage(contact.connection(), "%s: Your R&R forms have been sent from %s to MSD" % (contact.name(), contact.service_delivery_point.parent_service_delivery_point.name))
                m.send() 
            
            return
        elif service_delivery_point.service_delivery_point_type.name == "Facility":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_submitted_facility_to_district")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.datetime.now())
            ns.save()
            self.respond('Thank you %s for submitting your R&R form for facility %s' % (self.msg.contact.name,self.msg.contact.contactdetail.service_delivery_point.name))
            return
        else:
            self.respond("Sorry, but we don't know who you are!")
        

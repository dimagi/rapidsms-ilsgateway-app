#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ContactDetail, DeliveryGroup
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
import datetime
from ilsgateway.utils import *

class ConfirmRandRSubmitted(KeywordHandler):
    keyword = "sub|submitted"
    def help(self):
        self.respond("Please respond in the format \"submitted a 12 b 10 c 2.\"")

    def handle(self, text):
        service_delivery_point=self.msg.contact.contactdetail.service_delivery_point
        if service_delivery_point.service_delivery_point_type.name == "DISTRICT":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_submitted_district_to_msd")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
            ns.save()
            
            delivery_groups_list = text.split()
            if len(delivery_groups_list) > 0 and len(delivery_groups_list) % 2 != 0:
                 self.respond("Sorry, invalid format.  The message should be in the format \"submitted a 12 b 10 c 2.\"")
                 return
            else:    
                sdp = self.msg.contact.contactdetail.service_delivery_point
                while len(delivery_groups_list) >= 2:
                    quantity = delivery_groups_list.pop(0)
                    if not is_number(quantity):
                        self.respond("%s is not a number" % quantity )
                        return
                                        
                    delivery_group_name = delivery_groups_list.pop(0)
                    try:
                        delivery_group = DeliveryGroup.objects.filter(name__iexact=delivery_group_name)[0:1].get()   
                    except DeliveryGroup.DoesNotExist:
                        self.respond('Sorry, invalid Delivery Group %s.  Please try again.' % delivery_group_name)
                        return
                    if float(quantity) > 2:
                        self.respond("You reported %s forms submitted for group %s, which is more than the number of facilities in group %s.  Please try again." % (quantity, delivery_group_name, delivery_group_name) )
                        return

                    sdp.report_delivery_group_status(delivery_group=delivery_group,quantity=quantity, message=self.msg.logger_msg)
            
            self.respond('Thank you %s for reporting your R&R form submissions for %s' % (self.msg.contact.name,self.msg.contact.contactdetail.service_delivery_point.name))
#            contacts_to_notify = ContactDetail.objects.filter(parent_id=service_delivery_point.id, primary=True, service_delivery_point__delivery_group__name='A')
#            for contact in contacts_to_notify:
#                m = OutgoingMessage(contact.connection(), "%s: Your R&R forms have been sent from %s to MSD" % (contact.name(), contact.service_delivery_point.parent_service_delivery_point.name))
#                m.send() 
            
            return
        elif service_delivery_point.service_delivery_point_type.name == "FACILITY":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_submitted_facility_to_district")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
            ns.save()
            self.respond('Thank you %s for submitting your R and R form for %s' % (self.msg.contact.name,self.msg.contact.contactdetail.service_delivery_point.name))
            return
        else:
            self.respond("Sorry, but we don't know who you are!")
        

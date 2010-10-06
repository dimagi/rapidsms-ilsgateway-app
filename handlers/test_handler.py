#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ProductReportType, Product
from datetime import *
from ilsgateway.utils import current_submitting_group
        
class TestReminder(KeywordHandler):
    """
    """

    keyword = "test"

    def help(self):
        self.respond("To test a reminder, send \"test reminder [remindername]\"; valid tests are soh, delivery, randr. Remember to setup your contact details!")

    def handle(self, text):
        if text == "reminder soh":
            contact_detail = self.msg.contact.contactdetail
            default_connection = contact_detail.default_connection
            if default_connection:
                m = OutgoingMessage(default_connection, "Please send in your stock on hand information in the format \"soh inj 200 con 300 imp 10 pop 320 coc 232 iud 10\"")
                m.send() 
                st = ServiceDeliveryPointStatusType.objects.filter(short_name="soh_reminder_sent_facility")[0:1].get()
                ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                ns.save()
        elif text == "reminder randr":
            contact_detail = self.msg.contact.contactdetail
            default_connection = contact_detail.default_connection
            if default_connection:
                m = OutgoingMessage(default_connection, "Have you sent in your R&R form yet for this quarter? Please reply \"submitted\" or \"not submitted\"")
                m.send() 
                st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_facility")[0:1].get()
                ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                ns.save()
        
        elif text == "reminder delivery":
            print self.msg.contact
            contact_detail = self.msg.contact.contactdetail
            default_connection = contact_detail.default_connection
            print default_connection
            if default_connection:
                if contact_detail.service_delivery_point.service_delivery_point_type.name == "FACILITY":
                    m = OutgoingMessage(default_connection, "Did you receive your delivery yet? Please reply \"delivered inj 200 con 300 imp 10 pop 320 coc 232 iud 10\" or \"not delivered\"")
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
                    
                elif contact_detail.service_delivery_point.service_delivery_point_type.name == "DISTRICT": 
                    m = OutgoingMessage(default_connection, "It's time to submit group %s. How many R&R forms have you submitted to MSD so far?  Reply with \"submitted 20 a 10 b 2 c\"." % current_submitting_group() )
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_district")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
                else:
                    self.respond("Sorry there was a problem with your service delivery point setup. Please check via the admin.")
        else:
            self.respond("Sorry I didn't understand. To test a reminder, send \"test reminder [remindername]\"; valid tests are soh, delivery, randr.")
                        
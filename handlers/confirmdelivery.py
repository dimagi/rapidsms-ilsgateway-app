#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType
import datetime
        
class ConfirmDeliveryReceived(KeywordHandler):
    """
    for reporting delivery confirmation, products and amounts
    """

    keyword = "dlvd"

    def help(self):
        #TODO needs some work on this message
        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received")[0:1].get()
        ns = ServiceDeliveryPointStatus(service_delivery_point=self.msg.contact.contactdetail.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond("To record a delivery, respond with DLVD product amount.  For example, dlvd con 500.")

    def handle(self, text):
        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_quantities_reported")[0:1].get()
        ns = ServiceDeliveryPointStatus(service_delivery_point=self.msg.contact.contactdetail.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond('Thank you %s for reporting your delivery of %s for %s' % (self.msg.contact.name, text, self.msg.contact.contactdetail.service_delivery_point.name))              
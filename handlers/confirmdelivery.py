#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ProductReportType, Product
import datetime
        
class ConfirmDeliveryReceived(KeywordHandler):
    """
    for reporting delivery confirmation, products and amounts
    """

    keyword = "dlvd"

    def help(self):
        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received")[0:1].get()
        ns = ServiceDeliveryPointStatus(service_delivery_point=self.msg.contact.contactdetail.service_delivery_point, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond("To record a delivery, respond with DLVD product amount.  For example, dlvd con 500.")

    def handle(self, text):
        product_list = text.split()
        if len(product_list) > 0 and len(product_list) % 2 != 0:
             self.respond("Sorry, invalid format.  The message should be in the format 'dlvd inj 200 con 344 imp 20'")
             return
        else:
            sdp = self.msg.contact.contactdetail.service_delivery_point
            while len(product_list) >= 2:
                product_code = product_list.pop(0)
                quantity = product_list.pop(0)
                report_type = ProductReportType.objects.filter(sms_code='dlvd')[0:1].get()
                try:
                    product = Product.objects.filter(sms_code__iexact=product_code)[0:1].get()   
                except Product.DoesNotExist:
                    self.respond('Sorry, invalid product code %s!' % product_code)
                    return
                
                sdp.report_product_status(product=product,report_type=report_type,quantity=quantity)
            
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_quantities_reported")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=sdp, status_type=st, status_date=datetime.datetime.now())
            ns.save()

            self.respond('Thank you %s for reporting your delivery of %s for %s' % (self.msg.contact.name, text, sdp.name))              
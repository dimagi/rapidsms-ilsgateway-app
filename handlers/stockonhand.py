#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPoint, Product, ProductReportType, ContactDetail
from ilsgateway.utils import *

class StockOnHandHandler(KeywordHandler):
    """
    """
    keyword = "soh"
    def help(self):
        self.respond("To report stock on hand, respond with \"soh product amount\".  For example, \"soh con 500\".")

    def handle(self, text):
        product_list = text.split()
        if len(product_list) > 0 and len(product_list) % 2 != 0:
             self.respond("Sorry, invalid format.  The message should be in the format \"soh inj 200 con 344 imp 20\"")
             return
        else:    
            sdp = self.msg.contact.contactdetail.service_delivery_point
            while len(product_list) >= 2:
                product_code = product_list.pop(0)
                quantity = product_list.pop(0)
                if not is_number(quantity):
                    if is_number(product_code):
                        temp = product_code
                        product_code = quantity
                        quantity = temp
                    else:                        
                        self.respond("Sorry, invalid format. The message should be in the format \"soh inj 200 con 344 imp 20\"")
                        return
                
                report_type = ProductReportType.objects.filter(sms_code='soh')[0:1].get()
                try:
                    product = Product.objects.filter(sms_code__iexact=product_code)[0:1].get()   
                except Product.DoesNotExist:
                    self.respond('Sorry, invalid product code %s!' % product_code)
                    return
                
                sdp.report_product_status(product=product,report_type=report_type,quantity=quantity, message=self.msg.logger_msg)
            
            self.respond('Thank you %s for reporting your stock on hand for %s!' % (self.msg.contact.name, sdp.name))              
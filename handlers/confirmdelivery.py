#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ProductReportType, Product
from datetime import *
from ilsgateway.utils import *
        
class ConfirmDeliveryReceived(KeywordHandler):
    """
    for reporting delivery confirmation, products and amounts
    """

    keyword = "delivered|dlvd"

    def help(self):
        service_delivery_point=self.msg.contact.contactdetail.service_delivery_point
        if service_delivery_point.service_delivery_point_type.name == "DISTRICT":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_district")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
            ns.save()
            self.respond('Thank you %s for reporting your delivery for %s' % (self.msg.contact.name, service_delivery_point.name))
        elif service_delivery_point.service_delivery_point_type.name == "FACILITY":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_facility")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
            ns.save()
            self.respond("To record a delivery, respond with \"delivered product amount product amount...\" For example, dlvd inj 200 con 300 imp 10 pop 320 coc 232 iud 10.")

    def handle(self, text):
        service_delivery_point=self.msg.contact.contactdetail.service_delivery_point
        if service_delivery_point.service_delivery_point_type.name == "DISTRICT":
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_district")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
            ns.save()
            self.respond('Thank you %s for reporting your delivery for %s' % (self.msg.contact.name, service_delivery_point.name))
        elif service_delivery_point.service_delivery_point_type.name == "FACILITY":
            product_list = text.split()
            if len(product_list) > 0 and len(product_list) % 2 != 0:
                 self.respond("Sorry, invalid format.  The message should be in the format 'dlvd inj 200 con 344 imp 20'")
                 return
            else:
                while len(product_list) >= 2:
                    product_code = product_list.pop(0)
                    quantity = product_list.pop(0)
                    if not is_number(quantity):
                        if is_number(product_code):
                            temp = product_code
                            product_code = quantity
                            quantity = temp
                        else:                        
                            self.respond("Sorry, invalid format. The message should be in the format \"dlvd inj 200 con 344 imp 20\"")
                            return
                    
                    report_type = ProductReportType.objects.filter(sms_code='dlvd')[0:1].get()
                    try:
                        product = Product.objects.filter(sms_code__iexact=product_code)[0:1].get()   
                    except Product.DoesNotExist:
                        self.respond('Sorry, invalid product code %s!' % product_code)
                        return
                    
                    service_delivery_point.report_product_status(product=product,report_type=report_type,quantity=quantity, message=self.msg.logger_msg)
                
                st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_quantities_reported")[0:1].get()
                ns = ServiceDeliveryPointStatus(service_delivery_point=service_delivery_point, status_type=st, status_date=datetime.now())
                ns.save()
    
                self.respond('Thank you %s for reporting your delivery for %s' % (self.msg.contact.name, service_delivery_point.name))              
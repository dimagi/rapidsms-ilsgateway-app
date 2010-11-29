#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import ServiceDeliveryPoint, Product, ProductReportType, ContactDetail, ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType
from ilsgateway.utils import *
from dateutil.relativedelta import *
from django.db.models import Q
from django.utils.translation import ugettext as _
from rapidsms.messages import OutgoingMessage

class StockOnHandHandler(KeywordHandler):
    """
    """
    keyword = "soh|hmk"
    def help(self):
        self.respond(_("Please send in your stock on hand information in the format 'soh <product> <amount> <product> <amount>...'"))

    def handle(self, text):
        product_list = text.split()
        if len(product_list) > 0 and len(product_list) % 2 != 0:
             self.respond(_("Sorry, invalid format.  The message should be in the format 'delivered product amount product amount'"))
             return
        else:    
            reported_products = []
            sdp = self.msg.contact.contactdetail.service_delivery_point
            reply_list = []
            while len(product_list) >= 2:
                product_code = product_list.pop(0)
                quantity = product_list.pop(0)
                if not is_number(quantity):
                    if is_number(product_code):
                        temp = product_code
                        product_code = quantity
                        quantity = temp
                    else:                        
                        self.respond(_("Sorry, invalid format.  The message should be in the format 'delivered product amount product amount'"))
                        return
                report_type = ProductReportType.objects.filter(sms_code='soh')[0:1].get()
                try:
                    product = Product.objects.filter(sms_code__iexact=product_code)[0:1].get()   
                except Product.DoesNotExist:
                    self.respond(_("Sorry, invalid product code %(code)s"), code=product_code.upper())
                    return
                reported_products.append(product.sms_code)
                reply_list.append('%s %s' % (product.sms_code, quantity) )
                sdp.report_product_status(product=product,report_type=report_type,quantity=quantity, message=self.msg.logger_msg)
            now = datetime.now()
            all_products = []
            date_check = datetime.now() + relativedelta(days=-7)
            missing_products = Product.objects.filter(Q(activeproduct__service_delivery_point=sdp, activeproduct__is_active=True), 
                                                      ~Q(servicedeliverypointproductreport__report_date__gt=date_check) )
            for dict in missing_products.values('sms_code'):
                all_products.append(dict['sms_code'])
            missing_product_list = list(set(all_products)-set(reported_products))
            if missing_product_list:
                kwargs = {'contact_name': self.msg.contact.name,
                          'facility_name': sdp.name,
                          'product_list': ', '.join(missing_product_list)}
                self.respond(_('Thank you %(contact_name)s for reporting your stock on hand for %(facility_name)s.  Still missing %(product_list)s.'), **kwargs)
            else:    
                self.respond(_('Thank you, you reported you have %(reply_list)s. If incorrect, please resend.'), reply_list=','.join(reply_list))
            self.respond(_("Please send in your adjustments in the format 'la <product> +-<amount> +-<product> +-<amount>...'"))
            st = ServiceDeliveryPointStatusType.objects.filter(short_name="lost_adjusted_reminder_sent_facility")[0:1].get()
            ns = ServiceDeliveryPointStatus(service_delivery_point=sdp, status_type=st, status_date=datetime.now())
            ns.save()
        
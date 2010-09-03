#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.pattern import PatternHandler
from ilsgateway.models import Node, Product, ProductReportType, ContactDetail

class StockOnHandHandler(PatternHandler):
    pattern = r'^(\w+) (\w+) (\d+)$'
    # TODO: better handling of non-registered senders - currently just fails
    def handle(self, a, b, c):
        report_types = ProductReportType.objects.filter(sms_code=a)
        if not report_types:
            self.respond_error
        else:
            n = self.msg.contact.contactdetail.node
            products = Product.objects.filter(sms_code=b) 
            if not products:
                self.respond_error
            else:            
                p = products[0]
                rt = report_types[0]
                q = int(c)
                n.report_product_status(product=p,report_type=rt,quantity=q)
                
                self.respond('%s recorded: %s %s by %s' % (rt.name, p.sms_code, c, self.msg.contact.name))       
#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.pattern import PatternHandler
from ilsgateway.models import NodeStatus, NodeStatusType
import datetime

class ConfirmRandRSubmitted(PatternHandler):
    pattern = r'^subm.*$'
    def handle(self):
        st = NodeStatusType.objects.filter(short_name="r_and_r_submitted")[0:1].get()
        ns = NodeStatus(node=self.msg.contact.contactdetail.node, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond('Thank you %s for submitting your R&R form for %s' % (self.msg.contact.name,self.msg.contact.contactdetail.node.name))

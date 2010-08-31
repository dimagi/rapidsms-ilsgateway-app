#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ilsgateway.models import NodeStatus, NodeStatusType
import datetime
        
class ConfirmDeliveryReceived(KeywordHandler):
    """
    Handle any message prefixed ``echo``, responding with the remainder
    of the text. Useful for remotely testing internationalization.
    """

    keyword = "dlvd"

    def help(self):
        #TODO needs some work on this message
        st = NodeStatusType.objects.filter(short_name="delivery_received")[0:1].get()
        ns = NodeStatus(node=self.msg.contact.contactdetail.node, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond("To record a delivery, respond with DLVD product amt...")

    def handle(self, text):
        st = NodeStatusType.objects.filter(short_name="delivery_quantities_reported")[0:1].get()
        ns = NodeStatus(node=self.msg.contact.contactdetail.node, status_type=st, status_date=datetime.datetime.now())
        ns.save()
        self.respond('Thank you %s for reporting your delivery of %s for %s' % (self.msg.contact.name, text, self.msg.contact.contactdetail.node.name))              
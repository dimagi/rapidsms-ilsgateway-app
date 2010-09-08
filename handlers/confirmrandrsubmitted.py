#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.pattern import PatternHandler
from ilsgateway.models import NodeStatus, NodeStatusType, ContactDetail
from rapidsms.models import Connection 
from rapidsms.messages import OutgoingMessage
import datetime

class ConfirmRandRSubmitted(PatternHandler):
    #todo: this should move up to the app level probably
    pattern = r'^subm.*$'
    def handle(self):
        node=self.msg.contact.contactdetail.node
        if node.node_type.name == "District":
            st = NodeStatusType.objects.filter(short_name="r_and_r_submitted_district_to_msd")[0:1].get()
            ns = NodeStatus(node=node, status_type=st, status_date=datetime.datetime.now())
            ns.save()
            self.respond('Thank you %s for submitting your R&R forms for district %s' % (self.msg.contact.name,self.msg.contact.contactdetail.node.name))
            contacts_to_notify = ContactDetail.objects.filter(node__parent_node__id=9, primary=True, node__delivery_group__name='A')
            for contact in contacts_to_notify:
                m = OutgoingMessage(contact.connection(), "%s: Your R&R forms have been sent from %s to MSD" % (contact.name(), contact.node.parent_node.name))
                m.send() 
            
            return
        elif node.node_type.name == "Facility":
            st = NodeStatusType.objects.filter(short_name="r_and_r_submitted_facility_to_district")[0:1].get()
            ns = NodeStatus(node=node, status_type=st, status_date=datetime.datetime.now())
            ns.save()
            self.respond('Thank you %s for submitting your R&R form for facility %s' % (self.msg.contact.name,self.msg.contact.contactdetail.node.name))
            return
        else:
            self.respond("Sorry, but we don't know who you are!")
        

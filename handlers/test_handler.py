#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from rapidsms.messages import OutgoingMessage
from ilsgateway.models import ServiceDeliveryPointStatus, ServiceDeliveryPointStatusType, ProductReportType, Product, ServiceDeliveryPoint, ContactDetail
from datetime import *
from ilsgateway.utils import current_submitting_group, current_delivering_group
from django.utils.translation import ugettext_noop as _
        
class TestReminder(KeywordHandler):
    """
    """

    keyword = "test|TEST"

    def help(self):
        self.respond(_("To test a reminder, send \"test [remindername] [msd code]\"; valid tests are soh, delivery, randr. Remember to setup your contact details!"))

    def handle(self, text):
        command, parameter = text.lower().split()
        sdp = ServiceDeliveryPoint.objects.get(msd_code=parameter.upper())
        contact_details_to_remind = ContactDetail.objects.filter(service_delivery_point=sdp)
        if not sdp:
            self.respond("Invalid msd code %s" % parameter)
            return
        if command in ['la']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, _("Please send in your adjustments in the format 'la <product> +-<amount> +-<product> +-<amount>...'"))
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="lost_adjusted_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
                    ns.save()
            self.respond("Sent")
        if command in ['supervision']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, _("Have you received supervision this month? Please reply 'supervision yes' or 'supervision no'"))
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="supervision_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
                    ns.save()
            self.respond("Sent")
        if command in ['soh','hmk']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    m = OutgoingMessage(default_connection, _("Please send in your stock on hand information in the format 'soh <product> <amount> <product> <amount>...'"))
                    m.send() 
                    st = ServiceDeliveryPointStatusType.objects.filter(short_name="soh_reminder_sent_facility")[0:1].get()
                    ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                    ns.save()
            self.respond("Sent")
        elif command in ['randr']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    if sdp.service_delivery_point_type.name == "DISTRICT":
                        m = OutgoingMessage(default_connection, _("How many R&R forms have you submitted to MSD? Reply with 'submitted A <number of R&Rs submitted for group A> B <number of R&Rs submitted for group B>'"))
                        m.send() 
                    elif sdp.service_delivery_point_type.name == "FACILITY":
                        m = OutgoingMessage(default_connection, _("Have you sent in your R&R form yet for this quarter? Please reply \"submitted\" or \"not submitted\""))
                        m.send() 
                        st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_facility")[0:1].get()
                        ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                        ns.save()        
            self.respond("Sent")
        elif command in ['delivery']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    if contact_detail.service_delivery_point.service_delivery_point_type.name == "FACILITY":
                        m = OutgoingMessage(default_connection, _("Did you receive your delivery yet? Please reply 'delivered <product> <amount> <product> <amount>...'"))
                        m.send() 
                        st = ServiceDeliveryPointStatusType.objects.filter(short_name="delivery_received_reminder_sent_facility")[0:1].get()
                        ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                        ns.save()
                    elif contact_detail.service_delivery_point.service_delivery_point_type.name == "DISTRICT": 
                        m = OutgoingMessage(default_connection, _("Did you receive your delivery yet? Please reply 'delivered' or 'not delivered'"))
                        m.send() 
                        st = ServiceDeliveryPointStatusType.objects.filter(short_name="r_and_r_reminder_sent_district")[0:1].get()
                        ns = ServiceDeliveryPointStatus(service_delivery_point=contact_detail.service_delivery_point, status_type=st, status_date=datetime.now())
                        ns.save()
                    else:
                        self.respond("Sorry there was a problem with your service delivery point setup. Please check via the admin.")
            self.respond("Sent")
        elif command in ['latedelivery']:
            for contact_detail in contact_details_to_remind:
                default_connection = contact_detail.default_connection
                if default_connection:
                    service_delivery_point = contact_detail.service_delivery_point
                    kwargs = {"group_name": current_delivering_group(), 
                              "group_total": service_delivery_point.child_sdps().filter(delivery_group__name=current_delivering_group()).count(), 
                              "not_responded_count": service_delivery_point.child_sdps_not_responded_delivery_this_month(), 
                              "not_received_count": service_delivery_point.child_sdps_not_received_delivery_this_month()}
                    m = OutgoingMessage(default_connection, 
                                        _("Facility deliveries for group %(group_name)s (out of %(group_total)d): %(not_responded_count)d haven't responded and %(not_received_count)d have reported not receiving. See ilsgateway.com"),
                                        **kwargs) 
                    m.send()         
            self.respond("Sent")
                        
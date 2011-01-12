from datetime import datetime, timedelta
from django.utils.translation import ugettext as _
from rapidsms.messages import OutgoingMessage

#temp
import logging


def crumb(service_delivery_point):
    return "<div><a href="">this is a test | </a></div>"
    
def end_of_month(month=datetime.now().month):
    if month == 12:
        next_month = 1
    else:
        next_month = month + 1
    return datetime(datetime.now().year, next_month, 1) - timedelta(seconds=1)

def beginning_of_month(month=datetime.now().month):
    return datetime(datetime.now().year, month, 1)    

def current_submitting_group():
    months = {1:"A", 2:"B", 3:"C", 4:"A", 5:"B", 6:"C", 7:"A", 8:"B", 9:"C", 10:"A", 11:"B", 12:"C",}    
    return months[datetime.now().date().month]

def current_processing_group():
    months = {2:"A", 3:"B", 4:"C", 5:"A", 6:"B", 7:"C", 8:"A", 9:"B", 10:"C", 11:"A", 12:"B", 1:"C",}    
    return months[datetime.now().date().month]    

def current_delivering_group():
    months = {3:"A", 4:"B", 5:"C", 6:"A", 7:"B", 8:"C", 9:"A", 10:"B", 11:"C", 12:"A", 1:"B", 2:"C",}    
    return months[datetime.now().date().month]    

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def get_message(contact_detail, msg_code, **kwargs):
    str = ''
    message_dict = {}
    if msg_code == "alert_parent_district_delivery_received_sent_facility":
        if kwargs['sdp']:                
            message_dict['district_name'] = kwargs['sdp'].name
            str = "District %(district_name)s has reported that they received their delivery from MSD."    
    if msg_code == "alert_parent_district_sent_randr":
        if kwargs['sdp']:                
            message_dict['district_name'] = kwargs['sdp'].name
            str = "District %(district_name)s has reported that they sent their R&R forms to MSD."    
    if msg_code == "lost_adjusted_reminder_sent_facility":
        str = "Please send in your adjustments in the format 'la <product> +-<amount> +-<product> +-<amount>...'"
    if msg_code == "soh_reminder_sent_facility":
        str = "Please send in your stock on hand information in the format 'soh <product> <amount> <product> <amount>...'"
    if msg_code == "r_and_r_reminder_sent_district":
        str=  "How many R&R forms have you submitted to MSD? Reply with 'submitted A <number of R&Rs submitted for group A> B <number of R&Rs submitted for group B>'"
    if msg_code == "delivery_received_reminder_sent_facility":
        str =  "Did you receive your delivery yet? Please reply 'delivered <product> <amount> <product> <amount>...'"
    if msg_code == "supervision_reminder_sent_facility":
        str =  "Have you received supervision this month? Please reply 'supervision yes' or 'supervision no'"
    if msg_code == "delivery_received_reminder_sent_district":
        str = "Did you receive your delivery yet? Please reply 'delivered' or 'not delivered'"
    if msg_code == "r_and_r_reminder_sent_facility":
        str = "Have you sent in your R&R form yet for this quarter? Please reply \"submitted\" or \"not submitted\""
    if msg_code == "alert_delinquent_delivery_sent_district":
        sdp = contact_detail.service_delivery_point
        message_dict = {
           'not_responded_count': sdp.child_sdps_not_responded_delivery_this_month(),
           'not_received_count': sdp.child_sdps_not_received_delivery_this_month()}
        total = sum([i for i in message_dict.values()])
        if total:
            message_dict['group_name'] = current_delivering_group()
            message_dict['group_total'] = sdp.child_sdps_receiving().count()
            str = "Facility deliveries for group %(group_name)s (out of %(group_total)d): %(not_responded_count)d haven't responded and %(not_received_count)d have reported not receiving. See ilsgateway.com"
        else:
            str = ''
    if str != '':
        m = OutgoingMessage(contact_detail.default_connection, str, **message_dict)
    else:
        m = None
    return m 
    
    
    
    
    
    
    
    
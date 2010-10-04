from datetime import datetime, timedelta

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
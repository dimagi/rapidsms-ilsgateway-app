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
    
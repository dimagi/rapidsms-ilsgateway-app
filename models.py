#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


from django.db import models
from django.db.models import Q
from rapidsms.models import ExtensibleModelBase
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User
from rapidsms.contrib.messagelog.models import Message
from datetime import datetime, timedelta
from utils import *
from django.contrib.contenttypes.models import ContentType
from dateutil.relativedelta import relativedelta
from django.db.models import Max
from re import match
from django.utils.translation import ugettext as _

class DeliveryGroupManager(models.Manager):    
    def get_by_natural_key(self, name):
        return self.get(name=name)    

class DeliveryGroup(models.Model):
    objects = DeliveryGroupManager()
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)  
            
class ServiceDeliveryPointNote(models.Model):
    text = models.CharField(max_length=500)
    service_delivery_point = models.ForeignKey('ServiceDeliveryPoint')
    created_at = models.DateTimeField(auto_now_add=True)
    contact_detail = models.ForeignKey('ContactDetail')
 
class Product(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)
    sms_code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
class ServiceDeliveryPointType(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name


class ActiveProduct(models.Model):
    is_active = models.BooleanField(default=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    service_delivery_point = models.ForeignKey('ServiceDeliveryPoint')
    product = models.ForeignKey('Product')

class ServiceDeliveryPointManager(models.Manager):    
    def get_by_natural_key(self, name):
        return self.get(name=name)    
    
class ServiceDeliveryPoint(Location):
    """
    ServiceDeliveryPoint - the main concept of a location.  Currently covers MOHSW, Regions, Districts and Facilities.  This could/should be broken out into subclasses.
    """
    @property
    def label(self):
        """
        Return an HTML fragment, for embedding in a Google map. This
        method should be overridden by subclasses wishing to provide
        better contextual information.
        """
        return unicode(self)
    
    def stock_levels_array(self):
        soh_array = []
        for product in Product.objects.all():
            if self.stock_on_hand(product.sms_code) == None:
                soh_value = "No data"
            else:
                soh_value = self.stock_on_hand(product.sms_code)
            if self.months_of_stock(product.sms_code) == None:
                mos_value = "Insufficient data"
            else:
                mos_value = self.months_of_stock(product.sms_code)
            soh_array.append([product.sms_code, soh_value, mos_value])
        return soh_array
    
    objects = ServiceDeliveryPointManager()
    name = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    delivery_group = models.ForeignKey(DeliveryGroup, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, through='ServiceDeliveryPointProductReport')
    msd_code = models.CharField(max_length=100, blank=True, null=True)
    service_delivery_point_type = models.ForeignKey(ServiceDeliveryPointType)
        
    def contacts(self, contact_type='all'):
        if contact_type == 'all':
            return ContactDetail.objects.filter(service_delivery_point=self)
        elif contact_type == 'primary':
            return ContactDetail.objects.filter(service_delivery_point=self, primary=True)
        elif contact_type == 'secondary':
            return ContactDetail.objects.filter(service_delivery_point=self, primary=False)
        else:
            return []

    def child_sdps_contacts(self):
        return ContactDetail.objects.filter(service_delivery_point__parent_id=self.id)        

    def primary_contacts(self):
        return self.contacts('primary')

    def secondary_contacts(self):
        return self.contacts('secondary')

    def received_reminder_after(self, short_name, date):
        result_set = self.servicedeliverypointstatus_set.filter(status_type__short_name=short_name, 
                                                      status_date__gt=date)
        if result_set:
            return True
        else:
            return False
    
    def report_product_status(self, **kwargs):
        npr = ServiceDeliveryPointProductReport(service_delivery_point = self,  **kwargs)
        npr.save()
        
    def report_delivery_group_status(self, **kwargs):
        sdp_dgr = ServiceDeliveryPointDGReport(service_delivery_point = self,  **kwargs)
        sdp_dgr.save()        
        
    def randr_status(self):
        status = self.servicedeliverypointstatus_set.filter(status_type__short_name__startswith='r_and_r').latest()
        return status
    
    def delivery_status(self):
        return self.servicedeliverypointstatus_set.filter(status_type__short_name__startswith='delivery').latest()  
        
    def get_products(self):
        return Product.objects.filter(servicedeliverypoint=self.id).distinct()
    
    def months_of_stock(self, sms_code):
        return None

    def last_message_received(self):
        reports = ServiceDeliveryPointProductReport.objects.filter(service_delivery_point__id=self.id, report_type__id=1).order_by('-report_date')
        if reports:
            return reports[0].message
        
    def child_sdps(self):
        return ServiceDeliveryPoint.objects.filter(parent_id=self.id)
    
    #Delivery
    def child_sdps_receiving(self):
        return self.child_sdps().filter(delivery_group__name=current_delivering_group())

    def child_sdps_received_delivery_this_month(self):
        return self._sdps_with_latest_status_this_month_is("delivery_received_facility").count() + \
               self._sdps_with_latest_status_this_month_is("delivery_quantities_reported").count()

    def child_sdps_not_received_delivery_this_month(self):
        return self._sdps_with_latest_status_this_month_is("delivery_not_received_facility").count()

    def child_sdps_not_responded_delivery_this_month(self):
        return self._sdps_with_latest_status_this_month_is("delivery_received_reminder_sent_facility").count()

    #R&R
    def child_sdps_submitting(self):
        return self.child_sdps().filter(delivery_group__name=current_submitting_group())

    def count_child_sdps_no_randr_reminder_sent(self,                                               
                                          start_time=datetime.now() + relativedelta(day=31, minute=59, second=59, hour=23, microsecond=999999, months=-1),
                                          end_time= datetime.now()):
        return self.child_sdps_submitting().exclude(servicedeliverypointstatus__status_type__short_name__startswith="r_and_r",
                                                    servicedeliverypointstatus__status_date__range=(start_time, end_time)).count()

    def child_sdps_submitted_randr_this_month(self):
        return self._sdps_with_latest_status_this_month_is("r_and_r_submitted_facility_to_district").count()

    def child_sdps_not_submitted_randr_this_month(self):
        return self._sdps_with_latest_status_this_month_is("r_and_r_not_submitted_facility_to_district").count()

    def child_sdps_not_responded_randr_this_month(self):
        return self._sdps_with_latest_status_this_month_is("r_and_r_reminder_sent_facility").count()

    def _sdps_with_latest_status_this_month_is(self, 
                                               status_short_name, 
                                               start_time=datetime.now() + relativedelta(day=31, minute=59, second=59, hour=23, microsecond=999999, months=-1),
                                               end_time= datetime.now()):
        if match('r_and_r', status_short_name):
            sdps = self.child_sdps_submitting()
            startswith = 'r_and_r'
        elif match('delivery', status_short_name):
            sdps = self.child_sdps_receiving()
            startswith = 'delivery'
        elif match('soh', status_short_name):
            sdps = self.child_sdps()
            startswith = 'soh'
        status_type_id = ServiceDeliveryPointStatusType.objects.get(short_name=status_short_name).id
        inner_qs = sdps.filter(servicedeliverypointstatus__status_date__range=(start_time, end_time),
                    servicedeliverypointstatus__status_type__short_name__startswith=startswith) \
                    .annotate(pk=Max('servicedeliverypointstatus__id'))
        sdp_status = ServiceDeliveryPointStatus.objects.filter(id__in=inner_qs.values('pk').query,
                                                               status_type__id=status_type_id).distinct()
        return sdp_status

    def child_sdps_processing_sent_to_msd(self, month=datetime.now().month):
        sdp_dgr_list = ServiceDeliveryPointDGReport.objects.filter(delivery_group__name=current_processing_group(), 
                                                                   report_date__range=( beginning_of_month(month), end_of_month(month) ),
                                                                   service_delivery_point__id=self.id )
        if not sdp_dgr_list:
            return 0
        else:
            return sdp_dgr_list[0].quantity
    
    def count_child_sdps_submitting_no_primary_contact(self):
        return self.child_sdps_submitting().count() - self.child_sdps_submitting().filter(contactdetail__primary=True).count()
    
    def child_sdps_processing(self):
        return self.child_sdps().filter(delivery_group__name=current_processing_group())

    #SOH
    def child_sdps_not_responded_soh_this_month(self):
        return self._sdps_with_latest_status_this_month_is("soh_reminder_sent_facility").count()
    
    def child_sdps_responded_soh(self, month=datetime.now().month):
        return self.child_sdps().filter(servicedeliverypointproductreport__report_date__range=( beginning_of_month(month), end_of_month(month) )).distinct().count()   
    
    def child_sdps_stocked_out(self, 
                               sms_code):
        inner_qs = self.child_sdps().filter(servicedeliverypointproductreport__product__sms_code=sms_code) \
                    .annotate(pk=Max('servicedeliverypointproductreport__id'))
        sdps = ServiceDeliveryPoint.objects.filter(servicedeliverypointproductreport__id__in=inner_qs.values('pk').query,
                                                   servicedeliverypointproductreport__quantity=0).distinct()
        return sdps
    
    def child_sdps_not_stocked_out(self, sms_code):
        return self.child_sdps().filter(servicedeliverypointproductreport__product__sms_code=sms_code,
                                        servicedeliverypointproductreport__quantity__gt=0,
                                        servicedeliverypointproductreport__report_date__range=( beginning_of_month(), end_of_month() )).distinct().count()
    
    def child_sdps_no_stock_out_data(self, sms_code):
        return self.child_sdps().count() - self.child_sdps_not_stocked_out(sms_code) - self.child_sdps_stocked_out(sms_code).count()

    def child_sdps_percentage_reporting_stock_this_month(self):
        if self.child_sdps().count() > 0:
            percentage = ( (self.child_sdps_responded_soh() * 100 ) / self.child_sdps().count() )
        else:
            percentage = 0  
        return "%d " % percentage

    def child_sdps_percentage_reporting_stock_last_month(self):
        now = datetime.now()
        if now.month == 1:
            last_month = 12
        else:
            last_month = now.month - 1

        if self.child_sdps().count() > 0:
            percentage = ( (self.child_sdps_responded_soh(last_month) * 100 ) / self.child_sdps().count() ) 
        else:
            percentage = 0
        return "%d " % percentage
    
    def stock_on_hand(self, sms_code):
        reports = ServiceDeliveryPointProductReport.objects.filter(service_delivery_point__id=self.id,
                                                product__sms_code=sms_code,
                                                report_type__id=1) 
        if reports:
            return reports[0].quantity                                 
        else:
            return None        
    
    def stock_on_hand_last_reported(self):
        reports = ServiceDeliveryPointProductReport.objects.filter(service_delivery_point__id=self.id,
                                                report_type__id=1) 
        if reports:
            return reports[0].report_date                                 
        elif self.received_reminder_after("soh_reminder_sent_facility", 
                                          datetime.now() + relativedelta(day=31, minute=59, second=59, hour=23, microsecond=999999, months=-1)):
            return "Waiting for reply"           
        else:
            return "No reminder sent"       

    def child_sdps_without_contacts(self):
        return self.child_sdps().filter(contactdetail__primary__isnull=True).order_by('name')[:3]

    def __unicode__(self):
        return self.name

class MinistryOfHealth(ServiceDeliveryPoint):
    class Meta:
        verbose_name_plural = "Ministry of Health"  

    pass
    
class Region(ServiceDeliveryPoint):
    pass

class District(ServiceDeliveryPoint):
    pass

class Facility(ServiceDeliveryPoint):
    class Meta:
        verbose_name_plural = "Facilities"  
    
    pass
    
class ContactRole(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Role"

    def __unicode__(self):
        return _(self.name)

class ContactDetail(Contact):
    user = models.OneToOneField(User, null=True, blank=True)
    role = models.ForeignKey(ContactRole, null=True, blank=True)
    email = models.EmailField(blank=True)
    #TODO validate only one primary can exist (or auto change all others to non-primary when new primary selected)
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint,null=True,blank=True)
    primary = models.BooleanField(default=False)
    
    def phone(self):
        if self.default_connection:
            return self.default_connection.identity
        else:
            return " "
    
    def role_name(self):
        return self.role.name

    def service_delivery_point_name(self):
        return self.service_delivery_point.name
    
    class Meta:
        verbose_name = "Contact Detail"
    
    def __unicode__(self):
        return self.name
        
class ProductReportType(models.Model):
    name = models.CharField(max_length=100)
    sms_code = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Inventory Status Type" 
    
class ServiceDeliveryPointProductReport(models.Model):
    product = models.ForeignKey(Product)
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint)
    report_type = models.ForeignKey(ProductReportType)
    quantity = models.IntegerField()  
    report_date = models.DateTimeField(auto_now_add=True, default=datetime.now())
    message = models.ForeignKey(Message)  
    
    def product_name(self):
        return self.product.name
    
    def service_delivery_point_name(self):
        return self.service_delivery_point.name

    def report_type_name(self):
        return self.report_type.name

    def __unicode__(self):
        return self.service_delivery_point.name + '-' + self.product.name + '-' + self.report_type.name

    class Meta:
        verbose_name = "Inventory Status Report" 
        ordering = ('-report_date',)

class ServiceDeliveryPointDGReport(models.Model):
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint)
    quantity = models.IntegerField()  
    report_date = models.DateTimeField(auto_now_add=True, default=datetime.now())
    message = models.ForeignKey(Message)  
    delivery_group = models.ForeignKey(DeliveryGroup)
    
    class Meta:
        ordering = ('-report_date',)
        
class ServiceDeliveryPointStatusType(models.Model):
    """
    This is the status for both R&R process and delivery - could be given a process name field to clarify between the two.
    """
    
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Facility Status Type"

    def __unicode__(self):
        return self.name    

class ServiceDeliveryPointStatus(models.Model):
    status_type = models.ForeignKey(ServiceDeliveryPointStatusType)
    #message = models.ForeignKey(Message)
    status_date = models.DateTimeField()
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint) 
        
    def status_type_name(self):
        return self.status_type.name
    
    def service_delivery_point_name(self):
        return self.service_delivery_point.name
    
    def __unicode__(self):
        return self.status_type.name
    
    class Meta:
        verbose_name = "Facility Status"
        verbose_name_plural = "Facility Statuses"  
        get_latest_by = "status_date"  
        ordering = ('-status_date',) 
#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


from django.db import models
from rapidsms.models import ExtensibleModelBase
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User
from rapidsms.messages import IncomingMessage
import datetime

class DeliveryGroup(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)  
    
class ServiceDeliveryPointType(models.Model):
    name = models.CharField(max_length=100, blank=True)
    parent_service_delivery_point_type = models.ForeignKey("self", null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = "ILS Level"      
        
class Product(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)
    sms_code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class ServiceDeliveryPointManager(models.Manager):    
    def get_by_natural_key(self, name):
        return self.get(name=name)    
    
class ServiceDeliveryPoint(models.Model):
    objects = ServiceDeliveryPointManager()

    service_delivery_point_type = models.ForeignKey(ServiceDeliveryPointType, null=True, blank=True)
    parent_service_delivery_point = models.ForeignKey("self", null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, unique=True)
    active = models.BooleanField(default=True)
    delivery_group = models.ForeignKey(DeliveryGroup, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, through='ServiceDeliveryPointProductReport')
    msd_code = models.CharField(max_length=100, blank=True, null=True)

    def service_delivery_point_type_name(self):
        return self.service_delivery_point_type
    
    def report_product_status(self, **kwargs):
        npr = ServiceDeliveryPointProductReport(service_delivery_point = self,  **kwargs)
        npr.save()
        
    def randr_status(self):
        return self.servicedeliverypointstatus_set.filter(status_type__short_name__startswith='r_and_r').latest()
    
    def delivery_status(self):
        return self.servicedeliverypointstatus_set.filter(status_type__short_name__startswith='delivery').latest()  
        
    def current_status(self):
        #TODO catch when no status exists
        return self.servicedeliverypointstatus_set.latest()
    
    def get_products(self):
        return Product.objects.filter(servicedeliverypoint=self.id).distinct()
    
    def months_of_stock(self, product):
        return 10

    #As soon as I learn how to create dynamic methods these are gone        
    def months_of_stock_inj(self):
        return self.months_of_stock('inj')

    def months_of_stock_pop(self):
        return self.months_of_stock('pop')

    def months_of_stock_coc(self):
        return self.months_of_stock('coc')

    def months_of_stock_imp(self):
        return self.months_of_stock('imp')

    def months_of_stock_con(self):
        return self.months_of_stock('con')

    def months_of_stock_iud(self):
        return self.months_of_stock('iud')
    
    def last_submitted_randr_date(self):
        return "2010-10-1"
    
    def stock_on_hand(self, sms_code):
        reports = ServiceDeliveryPointProductReport.objects.filter(service_delivery_point__id=self.id,
                                                product__sms_code=sms_code,
                                                report_type__id=1) 
        if reports:
            return reports[0].quantity                                 
        else:
            return "Waiting for reply"        
    
    def stock_on_hand_last_reported(self):
        reports = ServiceDeliveryPointProductReport.objects.filter(service_delivery_point__id=self.id,
                                                report_type__id=1) 
        if reports:
            return reports[0].report_date                                 
        else:
            return "Waiting for reply"                  
    
    #As soon as I learn how to create dynamic methods these are gone        
    def stock_on_hand_inj(self):
        return self.stock_on_hand('inj')

    def stock_on_hand_pop(self):
        return self.stock_on_hand('pop')

    def stock_on_hand_coc(self):
        return self.stock_on_hand('coc')

    def stock_on_hand_imp(self):
        return self.stock_on_hand('imp')

    def stock_on_hand_con(self):
        return self.stock_on_hand('con')

    def stock_on_hand_iud(self):
        return self.stock_on_hand('iud')

    def __unicode__(self):
        return self.name
    
class ContactRole(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Role"

    def __unicode__(self):
        return self.name

class ContactDetail(Contact):
    user = models.OneToOneField(User, null=True, blank=True)
    role = models.ForeignKey(ContactRole, null=True, blank=True)
    #TODO validate only one primary can exist (or auto change all others to non-primary when new primary selected)
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint,null=True,blank=True)
    primary = models.BooleanField(default=False)
    
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
    report_date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    #message = models.ForeignKey(IncomingMessage)  
    
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
        
class ServiceDeliveryPointStatusType(models.Model):
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
        
class ServiceDeliveryPointLocation(Location):
    service_delivery_point = models.ForeignKey(ServiceDeliveryPoint, null=True, blank=True)
    
    def __unicode__(self):
        """
        """
        return getattr(self, "name", "%s" % self.service_delivery_point.name)

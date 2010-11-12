#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib import admin
from rapidsms.admin import *
from ilsgateway.models import *
from rapidsms.models import Connection
from rapidsms.contrib.locations.models import Point

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_delivery_point_type_name')
    ordering = ['name']
        
class ConnectionInline(admin.TabularInline):
    model = Connection
    extra = 1
    
class ContactDetailAdmin(admin.ModelAdmin):
    model = ContactDetail
    list_display = ('name', 'role_name', 'service_delivery_point_name', 'primary')
    inlines = [
        ConnectionInline,
    ]

class ContactRoleAdmin(admin.ModelAdmin):
    model = ContactRole
    
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'units', 'sms_code', 'description','product_code')

class ProductReportTypeAdmin(admin.ModelAdmin):
    model = ProductReportType
    list_display = ('name', 'sms_code')
    
class ServiceDeliveryPointProductReportAdmin(admin.ModelAdmin):
    model = ServiceDeliveryPointProductReport
    list_display = ('product_name', 'report_type_name', 'service_delivery_point_name', 'quantity', 'report_date')
    
class ServiceDeliveryPointStatusAdmin(admin.ModelAdmin):
    model = ServiceDeliveryPointStatus
    list_display = ('status_type_name', 'service_delivery_point_name', 'status_date')

class ServiceDeliveryPointStatusTypeAdmin(admin.ModelAdmin):
    model = ServiceDeliveryPointStatusType
    list_display = ('name', 'short_name')
    
class PointAdmin(admin.ModelAdmin):
    model = Point    

class FacilityAdmin(admin.ModelAdmin):
    model = Facility

class DistrictAdmin(admin.ModelAdmin):
    model = District

class RegionAdmin(admin.ModelAdmin):
    model = Region

class DeliveryGroupAdmin(admin.ModelAdmin):
    model = DeliveryGroup
    
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReportType, ProductReportTypeAdmin)
admin.site.register(ServiceDeliveryPointProductReport, ServiceDeliveryPointProductReportAdmin)
admin.site.register(ContactRole, ContactRoleAdmin)
admin.site.unregister(Contact)
admin.site.register(ContactDetail, ContactDetailAdmin)
admin.site.register(ServiceDeliveryPointStatus, ServiceDeliveryPointStatusAdmin)
admin.site.register(ServiceDeliveryPointStatusType, ServiceDeliveryPointStatusTypeAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(DeliveryGroup, DeliveryGroupAdmin)



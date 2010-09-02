#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib import admin
from ilsgateway.models import *
from rapidsms.models import Connection
from rapidsms.contrib.locations.models import Point

class NodeTypeAdmin(admin.ModelAdmin):
    model = NodeType

class ContactInline(admin.ModelAdmin):
    model = Contact

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type_name')
    ordering = ['name']
    
class ContactDetailAdmin(admin.ModelAdmin):
    model = ContactDetail
    list_display = ('name', 'role_name', 'node_name', 'primary')

class ContactRoleAdmin(admin.ModelAdmin):
    model = ContactRole
    
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'units', 'sms_code', 'description','product_code')

class ProductReportTypeAdmin(admin.ModelAdmin):
    model = ProductReportType
    list_display = ('name', 'sms_code')
    
class NodeProductReportAdmin(admin.ModelAdmin):
    model = NodeProductReport
    list_display = ('product_name', 'report_type_name', 'node_name', 'quantity', 'report_date')
    
class NodeStatusAdmin(admin.ModelAdmin):
    model = NodeStatus
    list_display = ('status_type_name', 'node_name', 'status_date')

class NodeStatusTypeAdmin(admin.ModelAdmin):
    model = NodeStatusType
    list_display = ('name', 'short_name')
    
class PointAdmin(admin.ModelAdmin):
    model = Point    

class NodeLocationAdmin(admin.ModelAdmin):
    model = NodeLocation

class DeliveryGroupAdmin(admin.ModelAdmin):
    model = DeliveryGroup
    
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReportType, ProductReportTypeAdmin)
admin.site.register(NodeProductReport, NodeProductReportAdmin)
admin.site.register(NodeType, NodeTypeAdmin)
admin.site.register(ContactRole, ContactRoleAdmin)
admin.site.register(ContactDetail, ContactDetailAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(NodeStatus, NodeStatusAdmin)
admin.site.register(NodeStatusType, NodeStatusTypeAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(NodeLocation, NodeLocationAdmin)
admin.site.register(DeliveryGroup, DeliveryGroupAdmin)



#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


from django.db import models
from rapidsms.models import ExtensibleModelBase
from rapidsms.contrib.locations.models import Point
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User
from rapidsms.messages import IncomingMessage
import datetime

class NodeType(models.Model):
    name = models.CharField(max_length=100, blank=True)
    child_node_types = models.ManyToManyField("self", symmetrical=False, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = "ILS Level"  
    
class NodeBase(models.Model):
    node_type = models.ForeignKey(NodeType, null=True, blank=True)
    child_node = models.ManyToManyField("self", symmetrical=True, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    location = models.ForeignKey(Point, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def node_type_name(self):
        return self.node_type

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

#    def __repr__(self):
#        return "<Person #%r>" % (
#            self.pk or "??")

    def lookup(self, location=None):
        pass
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)
    sms_code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100, null=True, blank=True)\
    
    def __unicode__(self):
        return self.name
    
class Node(NodeBase):
    __metaclass__ = ExtensibleModelBase
    products = models.ManyToManyField(Product, through='NodeProductReport')

    class Meta:
        verbose_name = "System Node"
    
    def report_product_status(self, **kwargs):
        npr = NodeProductReport(node = self,  **kwargs)
        npr.save()
        
    def current_status(self):
        #TODO catch when no status exists
        return self.nodestatus_set.latest()
    
class ContactRole(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Role"

    def __unicode__(self):
        return self.name

class ContactDetail(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    role = models.ForeignKey(ContactRole, null=True, blank=True)
    #TODO validate only one primary can exist (or auto change all others to non-primary when new primary selected)
    node = models.ForeignKey(Node,null=True)
    contact = models.OneToOneField(Contact)
    primary = models.BooleanField(default=False)
    
    def name(self):
        return self.contact.name
    
    def role_name(self):
        return self.role.name

    def node_name(self):
        return self.node.name
    
    class Meta:
        verbose_name = "Contact Detail"
    
    def __unicode__(self):
        return self.contact.name
    
    def connection(self):
        return Connection.objects.filter(contact__id__exact=self.contact.id)[0]
    
class ProductReportType(models.Model):
    name = models.CharField(max_length=100)
    sms_code = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Inventory Status Type" 
    
class NodeProductReport(models.Model):
    product = models.ForeignKey(Product)
    node = models.ForeignKey(Node)
    report_type = models.ForeignKey(ProductReportType)
    quantity = models.IntegerField()  
    report_date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    #message = models.ForeignKey(IncomingMessage)  
    
    def product_name(self):
        return self.product.name
    
    def node_name(self):
        return self.node.name

    def report_type_name(self):
        return self.report_type.name

    def __unicode__(self):
        return self.node.name + '-' + self.product.name + '-' + self.report_type.name

    class Meta:
        verbose_name = "Inventory Status Report" 
        
class NodeStatusType(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Facility Status Type"

    def __unicode__(self):
        return self.name    

class NodeStatus(models.Model):
    status_type = models.ForeignKey(NodeStatusType)
    #message = models.ForeignKey(Message)
    status_date = models.DateTimeField()
    node = models.ForeignKey(Node) 
    
    def status_type_name(self):
        return self.status_type.name
    
    def node_name(self):
        return self.node.name
    
    def __unicode__(self):
        return self.status_type.name
    
    class Meta:
        verbose_name = "Facility Status"
        verbose_name_plural = "Facility Statuses"  
        get_latest_by = "status_date"  
        ordering = ('-status_date',)
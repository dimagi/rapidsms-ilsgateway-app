#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ilsgateway.views.dashboard'),                       
    (r'^facilities/(?P<facility_id>\d+)/$', 'ilsgateway.views.facilities_detail'),
    ('^facilities/(?P<view_type>\w+)/$', 'ilsgateway.views.facilities_index'),
    ('^facilities/ordering$', 'ilsgateway.views.facilities_ordering'),
    ('^districts$', 'ilsgateway.views.districts_index'),
    #(r'^districts/(?P<district_id>\d+)/$', 'ilsgateway.views.districts_detail'),
    (r'^doclist', 'ilsgateway.views.doclist'),
    (r'^docdownload', 'ilsgateway.views.docdownload'),
    url(r'^districts/(?P<district_id>\d*)/?$', "ilsgateway.views.districts_detail", name="districts_detail"),
    (r'^change_language', 'ilsgateway.views.change_language'),
    (r'^i18n/', include('django.conf.urls.i18n')),    
)

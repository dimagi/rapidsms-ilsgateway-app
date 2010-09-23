#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ilsgateway.views.dashboard'),                       
    (r'^facilities/(?P<facility_id>\d+)/$', 'ilsgateway.views.facilities_detail'),
    (r'^facilities/(?P<facility_id>\d+)/inventory/$', 'ilsgateway.views.facilities_detail', {'view_type': 'inventory'}),
    (r'^facilities/(?P<facility_id>\d+)/months_of_stock/$', 'ilsgateway.views.facilities_detail', {'view_type': 'months_of_stock'}),
    (r'^facilities/(?P<facility_id>\d+)/message_history/$', 'ilsgateway.views.message_history'),
    ('^facilities/inventory/$', 'ilsgateway.views.facilities_index', {'view_type': 'inventory'}),
    ('^facilities/months_of_stock/$', 'ilsgateway.views.facilities_index', {'view_type': 'months_of_stock'}),
    ('^facilities/ordering$', 'ilsgateway.views.facilities_ordering'),
    ('^districts$', 'ilsgateway.views.districts_index'),
    (r'^doclist', 'ilsgateway.views.doclist'),
    (r'^docdownload/(?P<msd_code>\w+)/$', 'ilsgateway.views.docdownload'),
    url(r'^districts/(?P<district_id>\d*)/?$', "ilsgateway.views.districts_detail", name="districts_detail"),
    (r'^change_language', 'ilsgateway.views.change_language'),
    (r'^i18n/', include('django.conf.urls.i18n')),  
)

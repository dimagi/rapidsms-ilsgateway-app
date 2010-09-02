#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ilsgateway.views.dashboard'),                       
    ('^facilities$', 'ilsgateway.views.facilities_index'),
    (r'^facilities/(?P<facility_id>\d+)/$', 'ilsgateway.views.facilities_detail'),
    ('^districts$', 'ilsgateway.views.districts_index'),
    (r'^districts/(?P<district_id>\d+)/$', 'ilsgateway.views.districts_detail'),
    (r'^scanning$', 'ilsgateway.views.scanning_test'),
    (r'^scanning_query$', 'ilsgateway.views.scanning_query'),
)

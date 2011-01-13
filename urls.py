#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ilsgateway.views.dashboard'),                       
    (r'^facilities/(?P<facility_id>\d+)/$', 'ilsgateway.views.facilities_detail'),
    (r'^facilities/(?P<facility_id>\d+)/inventory/$', 'ilsgateway.views.facilities_detail', {'view_type': 'inventory'}),
    (r'^facilities/(?P<facility_id>\d+)/months_of_stock/$', 'ilsgateway.views.facilities_detail', {'view_type': 'months_of_stock'}),
    (r'^facilities/(?P<facility_id>\d+)/message_history/$', 'ilsgateway.views.message_history'),
    (r'^facilities/(?P<facility_id>\d+)/note_history/$', 'ilsgateway.views.note_history'),
    ('^facilities/inventory/$', 'ilsgateway.views.facilities_index', {'view_type': 'inventory'}),
    ('^facilities/months_of_stock/$', 'ilsgateway.views.facilities_index', {'view_type': 'months_of_stock'}),
    url('^facilities/ordering$', 'ilsgateway.views.facilities_ordering', name="ordering"),
    url('^accounts/$', 'ilsgateway.views.password_change', name="password_change"),
    url('^accounts$', 'ilsgateway.views.password_change', name="password_change"),
    (r'^accounts/password_change_done/$', 'ilsgateway.views.password_change_done'),    
    (r'^doclist', 'ilsgateway.views.doclist'),
    (r'^supervision', 'ilsgateway.views.supervision'),
    (r'^stockinquiry', 'ilsgateway.views.stock_inquiry'),
    (r'^docdownload/(?P<facility_id>\w+)/$', 'ilsgateway.views.docdownload'),
    (r'^change_language', 'ilsgateway.views.change_language'),
    (r'^select_location', 'ilsgateway.views.select_location'),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^accounts/password_reset/$', 'ilsgateway.views.password_reset'),
    (r'^accounts/password_reset/done/$', 'ilsgateway.views.password_reset_done'),
    (r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'ilsgateway.views.password_reset_confirm'),
    (r'^accounts/reset/done/$', 'ilsgateway.views.password_reset_complete'),    
    (r'^accounts/sms_password/done/$', 'ilsgateway.views.sms_password_complete'),
)

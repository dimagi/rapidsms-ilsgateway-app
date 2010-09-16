#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime
from ilsgateway.models import ServiceDeliveryPoint, Product
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

#test
from httplib import HTTPSConnection, HTTPConnection
from BeautifulSoup import BeautifulStoneSoup
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

#xml test
from xml.etree import ElementTree

def change_language(request):
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    elif request.LANGUAGE_CODE == 'es':
        language = 'Spanish'        
    
    return render_to_response('change_language.html',
                              {'test_phrase': _('hello'),
                               'language': language},
                              context_instance=RequestContext(request))
    
@login_required
def dashboard(request):
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    elif request.LANGUAGE_CODE == 'es':
        language = 'Spanish'        
    
    sdp = ServiceDeliveryPoint.objects.filter(contactdetail__user__id=request.user.id)[0:1].get()
    return render_to_response('ilsgateway_dashboard.html',
                              {'sdp': sdp,
                               'language': language},
                              context_instance=RequestContext(request))

@login_required
def facilities_index(request, view_type='inventory'):
    sdp = ServiceDeliveryPoint.objects.filter(contactdetail__user__id=request.user.id)[0:1].get()
    facilities = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name__iexact="facility", parent_service_delivery_point=sdp).order_by("delivery_group")
    products = Product.objects.all()
    return render_to_response("facilities_list.html", 
                              {"facilities": facilities,
                               "products": products,
                               "sdp": sdp,
                               "view_type": view_type },
                              context_instance=RequestContext(request),)

@login_required
def facilities_ordering(request):
    sdp = ServiceDeliveryPoint.objects.filter(contactdetail__user__id=request.user.id)[0:1].get()
    facilities = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name__iexact="facility", parent_service_delivery_point=sdp)
    products = Product.objects.all()
    return render_to_response("facilities_ordering.html", 
                              {"facilities": facilities,
                               "products": products,
                               "sdp": sdp},
                              context_instance=RequestContext(request),)

@login_required
def facilities_detail(request, facility_id):
    try:
        f = ServiceDeliveryPoint.objects.get(pk=facility_id)
    except ServiceDeliveryPoint.DoesNotExist:
        raise Http404

    products = Product.objects.all()
    return render_to_response('facilities_detail.html', {'facility': f,
                                                         'products': products},
                              context_instance=RequestContext(request),)

@login_required    
def districts_index(request):
    #TODO filter
    districts = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name__iexact="District", order_by="delivery_group_id")
    return render_to_response("districts_list.html", {"districts": districts },
                              context_instance=RequestContext(request),)

@login_required
def districts_detail(request, district_id):
    try:
        d = ServiceDeliveryPoint.objects.get(pk=district_id)
    except ServiceDeliveryPoint.DoesNotExist:
        raise Http404
    
    facilities = ServiceDeliveryPoint.objects.filter(parent_service_delivery_point__id=district_id)
    products = Product.objects.all()
    return render_to_response('districts_detail.html', {'district': d,
                                                        'facilities': facilities, 
                                                        'products' : products,},
                                                        context_instance=RequestContext(request),)
        
def gdata_required(f):
    """
    Authenticate against Google GData service
    """
    def wrap(request, *args, **kwargs):
        if 'token' not in request.GET and 'token' not in request.session:
            # no token at all, request one-time-token
            # next: where to redirect
            # scope: what service you want to get access to
            return HttpResponseRedirect("https://www.google.com/accounts/AuthSubRequest?next=http://ilsgateway.dimagi.com/scanning_query&scope=scope=https://docs.google.com/feeds/%20http://spreadsheets.google.com/feeds/%20https://docs.googleusercontent.com/&session=1")
        elif 'token' not in request.session and 'token' in request.GET:
            # request session token using one-time-token
            conn = HTTPSConnection("www.google.com")
            conn.putrequest('GET', '/accounts/AuthSubSessionToken')
            conn.putheader('Authorization', 'AuthSub token="%s"' % request.GET['token'])
            conn.endheaders()
            conn.send(' ')
            r = conn.getresponse()
            if str(r.status) == '200':
                token = r.read()
                token = token.split('=')[1]
                token = token.replace('', '')
                request.session['token'] = token
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

@gdata_required
def scanning_test(request):
    """
    Simple example - list google docs documents
    """
    if 'token' in request.session:
        con = HTTPConnection("docs.google.com")
        con.putrequest('GET', '/feeds/documents/private/full/')
        con.putheader('Authorization', 'AuthSub token="%s"' % request.session['token'])
        con.endheaders()
        con.send('')
        r2 = con.getresponse()
        dane = r2.read()
        soup = BeautifulStoneSoup(dane)
        dane = soup.prettify()
        return render_to_response('a.html', {'dane':dane}, context_instance=RequestContext(request))
    else:
        return render_to_response('a.html', {'dane':'bad bad'}, context_instance=RequestContext(request))

@gdata_required
def scanning_query(request):
    """
    Search in documents
    """
    if 'token' in request.session:
        if 'q' in request.GET:
            q = request.GET['q']
        else:
            q=''
        con = HTTPConnection("docs.google.com")
        con.putrequest('GET', '/feeds/documents/private/full/-/pdf?q=%s' % q)
        con.putheader('Authorization', 'AuthSub token="%s"' % request.session['token'])
        con.endheaders()
        con.send('')
        r2 = con.getresponse()
        dane = r2.read()
        soup = BeautifulStoneSoup(dane)
        dane = soup.prettify()
        return render_to_response('b.html', {'dane':dane}, context_instance=RequestContext(request))
    else:
        return render_to_response('b.html', {'dane':'bad bad'}, context_instance=RequestContext(request))    

def xml_test(request):
    with open('podcasts.opml', 'rt') as f:
        tree = ElementTree.parse(f)

    response = {}
    for service_delivery_point in tree.getiterator():
        print service_delivery_point.tag, service_delivery_point.attrib
        response[service_delivery_point.tag] = service_delivery_point.attrib

    return HttpResponse(response)
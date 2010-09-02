#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime
from ilsgateway.models import Node, Product
from django.http import Http404
from django.template import RequestContext

#test
from httplib import HTTPSConnection, HTTPConnection
from BeautifulSoup import BeautifulStoneSoup
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse


def dashboard(request):
    return render_to_response('ilsgateway_dashboard.html',
                              context_instance=RequestContext(request))

def facilities_index(request):
    facilities = Node.objects.filter(node_type__name="Facility")
    return render_to_response("facilities_list.html", {"facilities": facilities })

def facilities_detail(request, facility_id):
    try:
        f = Node.objects.get(pk=facility_id)
    except Node.DoesNotExist:
        raise Http404
    
    return render_to_response('facilities_detail.html', {'facility': f,})
    
def districts_index(request):
    #TODO filter
    districts = Node.objects.filter(node_type__name="District")
    return render_to_response("districts_list.html", {"districts": districts })

def districts_detail(request, district_id):
    try:
        d = Node.objects.get(pk=district_id)
    except Node.DoesNotExist:
        raise Http404
    
    facilities = Node.objects.filter(parent_node__id=district_id)
    products = Product.objects.all()
    return render_to_response('districts_detail.html', {'district': d,
                                                        'facilities': facilities, 
                                                        'products' : products,})
        

def gdata_required(f):
    """
    Authenticate against Google GData service
    """
    def wrap(request, *args, **kwargs):
        if 'token' not in request.GET and 'token' not in request.session:
            # no token at all, request one-time-token
            # next: where to redirect
            # scope: what service you want to get access to
            return HttpResponseRedirect("https://www.google.com/accounts/AuthSubRequest?next=http://ilsgateway.dimagi.com/&scope=http://docs.google.com/feeds/documents&session=1")
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
        con.putrequest('GET', '/feeds/documents/private/full/?q=%s' % q)
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

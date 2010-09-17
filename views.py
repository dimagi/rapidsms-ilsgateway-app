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

#gdata
import gdata.docs.data
import gdata.docs.client
import gdata.gauth

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
            return HttpResponseRedirect("https://www.google.com/accounts/AuthSubRequest?next=http://ilsgateway.dimagi.com/doclist&scope=https://docs.google.com/feeds/%20https://docs.googleusercontent.com/&session=1")
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
def doclist(request):
    """
    Simple example - list google docs documents
    """
    if 'token' in request.session:
	client = gdata.docs.client.DocsClient()
	client.ssl = True  # Force all API requests through HTTPS
	client.http_client.debug = False  # Set to True for debugging HTTP requests
	client.auth_token = gdata.gauth.AuthSubToken(request.session['token'])
	feed = client.GetDocList()

	print '\n'
	if not feed.entry:
    		print 'No entries in feed.\n'
  	for entry in feed.entry:
    		print entry.title.text.encode('UTF-8'), entry.GetDocumentType(), entry.resource_id.text

    	# List folders the document is in.
    	for folder in entry.InFolders():
      		print folder.title

        return render_to_response('a.html', {}, context_instance=RequestContext(request))

@gdata_required
def docdownload(request):
    """
    Simple example - download google docs document
    """
    if 'token' in request.session:
	#should be able to make this global
        client = gdata.docs.client.DocsClient()
        client.ssl = True  # Force all API requests through HTTPS
        client.http_client.debug = False  # Set to True for debugging HTTP requests
        client.auth_token = gdata.gauth.AuthSubToken(request.session['token'])
        feed = client.GetDocList()

        print '\n'
	lastdoc = None
        if not feed.entry:
                print 'No entries in feed.\n'
        for entry in feed.entry:
                print entry.title.text.encode('UTF-8'), entry.GetDocumentType(), entry.resource_id.text
		#client.Download(entry, '/home/dimagivm/projects/%s.pdf' % entry.title.text)
		last_doc = entry

        # List folders the document is in.
        for folder in entry.InFolders():
                print folder.title
	
	exportFormat = '&exportFormat=pdf'
	content = client.GetFileContent(uri=last_doc.content.src + exportFormat)
        response = HttpResponse(content, mimetype='application/pdf')
#	response['Content-Type'] = 'application/pdf'
#	response['mimetype']=
	response['Content-Disposition'] = 'inline; filename=%s' % last_doc.title.text
#	response.write(content)
        return HttpResponse(response)

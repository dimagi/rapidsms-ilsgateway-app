#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.shortcuts import render_to_response
from datetime import datetime, date
from ilsgateway.models import ServiceDeliveryPoint, Product, Facility, ServiceDeliveryPointStatus, ServiceDeliveryPointNote, ContactDetail, ILSGatewayCell
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from rapidsms.contrib.messagelog.models import Message
from utils import *
from forms import NoteForm, SelectLocationForm, StockInquiryForm, SelectProductForm
from ilsgateway.tables import MessageHistoryTable, CurrentStockStatusTable, CurrentMOSTable, OrderingTable
from django.contrib.auth.admin import UserAdmin
from django.views.decorators.csrf import csrf_protect
from httplib import HTTPSConnection, HTTPConnection
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
import iso8601
import re
from django.core.urlresolvers import reverse
import random
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from rapidsms.messages import OutgoingMessage
from dateutil.relativedelta import relativedelta

from django.utils.functional import curry
from rapidsms.contrib.ajax.utils import call_router


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
                              {'language': language},
                              context_instance=RequestContext(request))

# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and 
#   prompts for a new password
# - password_reset_complete shows a success message for the above

@csrf_protect
def password_reset(request, is_admin_site=False, template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        password_reset_form=PasswordResetForm, token_generator=default_token_generator,
        post_reset_redirect=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('ilsgateway.views.password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {}
            opts['use_https'] = request.is_secure()
            opts['token_generator'] = token_generator
            if is_admin_site:
                opts['domain_override'] = request.META['HTTP_HOST']
            else:
                opts['email_template_name'] = email_template_name
                if not Site._meta.installed:
                    opts['domain_override'] = RequestSite(request).domain
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))

def password_reset_done(request, template_name='accounts/password_reset_done.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

# Doesn't need csrf_protect since no-one can guess the URL
def password_reset_confirm(request, uidb36=None, token=None, template_name='accounts/password_reset_confirm.html',
                           token_generator=default_token_generator, set_password_form=SetPasswordForm,
                           post_reset_redirect=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('ilsgateway.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    context_instance = RequestContext(request)

    if token_generator.check_token(user, token):
        context_instance['validlink'] = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        context_instance['validlink'] = False
        form = None
    context_instance['form'] = form
    return render_to_response(template_name, context_instance=context_instance)

def password_reset_complete(request, template_name='accounts/password_reset_complete.html'):
    return render_to_response(template_name, context_instance=RequestContext(request,
                                                                             {'login_url': settings.LOGIN_URL}))

def sms_password_complete(request, template_name='accounts/sms_password_done.html'):
    contact_detail = ContactDetail.objects.get(user=request.user.ilsgatewayuser)    
    default_connection = contact_detail.default_connection
    if default_connection:    
        m = OutgoingMessage(default_connection, _("Your password is: password"))
        m.send() 
    return render_to_response(template_name, context_instance=RequestContext(request,
                                                                             {'login_url': settings.LOGIN_URL}))

@csrf_protect
@login_required
def password_change(request, template_name='accounts/password_change.html',
                    post_change_redirect=None, password_change_form=PasswordChangeForm):
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    if post_change_redirect is None:
        post_change_redirect = reverse('ilsgateway.views.password_change_done')
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    return render_to_response(template_name, {
        'form': form,
        'language': language,
    }, context_instance=RequestContext(request))

def password_change_done(request, template_name='accounts/password_change_done.html'):
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    return render_to_response(template_name, 
                              {'language': language}, 
                              context_instance=RequestContext(request))

@login_required
def supervision(request):
    sdp = _get_current_sdp(request)
    
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    elif request.LANGUAGE_CODE == 'es':
        language = 'Spanish'        
    breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], [_('Supervision'), ''] ]
    notes = ServiceDeliveryPointNote.objects.filter(service_delivery_point__parent_id=sdp.id).order_by('-created_at')
    return render_to_response('supervision.html',
                              {'language': language,
                               'breadcrumbs': breadcrumbs,
                               'notes': notes,
                               'sdp': sdp},
                              context_instance=RequestContext(request))
    
@login_required
def dashboard(request):
    form_action = request.get_full_path()
    month = int(request.GET.get('month', 0))
    year = int(request.GET.get('year', 0))
    now = datetime.now()
    if month == 0:
        month = now.month 
            
    if year == 0:
        year = now.year 
        
    if year == now.year and month == datetime.now().month:
        show_next_month = False
    else:
        show_next_month = True
    report_date = date(year, month, now.day)
    month_name = report_date.strftime('%B')
    #this can't be right
    next_month_date = report_date + relativedelta(months=+1)
    previous_month_date = report_date + relativedelta(months=-1)
    next_month_link = "/?month=%d&year=%d" % (next_month_date.month, next_month_date.year)
    previous_month_link = "/?month=%d&year=%d" % (previous_month_date.month, previous_month_date.year) 
    contact_detail = ContactDetail.objects.get(user=request.user.ilsgatewayuser)
    #TODO this should be based on values in the DB
    is_allowed_to_change_location = False
    if _get_role(request).id in [3,5,6]:
        is_allowed_to_change_location = True
            
    #endTODO
    my_sdp = _get_my_sdp(request)
    if request.session.get('products'):
        products = request.session.get('products')
    else:
        products = Product.objects.all()
    dict = {} 
    for product in products: 
        dict[product.id] = True 
    select_product_form = SelectProductForm(initial={'products': dict,})
    if request.method == 'POST': 
        if 'change_product' in request.POST:
            select_product_form = SelectProductForm(data=request.POST)
            if select_product_form.is_valid():
                products = select_product_form.cleaned_data['products']  
                request.session['products'] = products
            else:
                select_product_form = SelectProductForm({'products': dict,})          
        elif 'change_location' in request.POST:
            form = SelectLocationForm(data=request.POST,
                                      service_delivery_point = my_sdp) 
            if form.is_valid():
                sdp_id = form.cleaned_data['location']
                request.session['current_sdp_id'] = sdp_id      
    sdp = _get_current_sdp(request)
    form = SelectLocationForm(service_delivery_point = my_sdp,
                              initial={'location': sdp.id}) 
    language = ''
    if request.LANGUAGE_CODE == 'en':
        language = 'English'
    elif request.LANGUAGE_CODE == 'sw':
        language = 'Swahili'
    elif request.LANGUAGE_CODE == 'es':
        language = 'Spanish'        
    breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''] ]
    
    facilities_without_primary_contacts = sdp.child_sdps_without_contacts()
    counts = {}
    counts['current_submitting_group'] = sdp.child_sdps().filter(delivery_group__name=current_submitting_group(report_date.month) ).count()
    counts['current_processing_group'] = sdp.child_sdps().filter(delivery_group__name=current_processing_group(report_date.month) ).count()
    counts['current_delivering_group'] = sdp.child_sdps().filter(delivery_group__name=current_delivering_group(report_date.month)).count()
    counts['total'] = counts['current_submitting_group'] + counts['current_processing_group'] + counts['current_delivering_group']
    groups = {}
    groups['current_submitting_group'] = current_submitting_group(report_date.month)
    groups['current_processing_group'] = current_processing_group(report_date.month)
    groups['current_delivering_group'] = current_delivering_group(report_date.month)
    d1 = []
    d2 = []
    d3 = []
    ticks = []
    index = 1
    stockouts_by_product = []
    for product in products:
        stockouts_by_product.append([product.name, sdp.child_sdps_stocked_out(product.sms_code,
                                                                              report_date)])
        d1.append([index, sdp.child_sdps_stocked_out(product.sms_code,
                                                     report_date).count()])
        d2.append([index, sdp.child_sdps_not_stocked_out(product.sms_code,
                                                         report_date) ])
        d3.append([index, sdp.child_sdps_no_stock_out_data(product.sms_code,
                                                           report_date) ])
        ticks.append([ index, str( '<span title="%s">%s</span>' % (product.name, product.sms_code.upper()) ) ])
        index = index + 1
    bar_data = [
                          {"data" : d1,
                          "label": str(_("Stocked out")), 
                          "bars": { "show" : "true" },
                          "color": "red"  
                          },
                          {"data" : d2,
                          "label": str(_("Not Stocked out")), 
                          "bars": { "show" : "true" }, 
                          "color": "green"  
                          },
                          {"data" : d3,
                          "label": str(_("No Stock Data")), 
                          "bars": { "show" : "true" }, 
                          }
                  ]
    
    message_dates_dict = {}
    randr_inquiry_date = None
    soh_inquiry_date = None
    delivery_inquiry_date = None

    randr_statuses = ServiceDeliveryPointStatus.objects.filter(status_type__short_name="r_and_r_reminder_sent_facility", 
                                                               status_date__range=( beginning_of_month(report_date.month), end_of_month(report_date.month) ) )
    if randr_statuses:
        randr_inquiry_date = randr_statuses[0].status_date
          
    delivery_statuses = ServiceDeliveryPointStatus.objects.filter(status_type__short_name="delivery_received_reminder_sent_facility", 
                                                                  status_date__range=( beginning_of_month(report_date.month), end_of_month(report_date.month) ) )
    if delivery_statuses:
        delivery_inquiry_date = delivery_statuses[0].status_date

    monthly_data = {'submitted': sdp.child_sdps_submitted_randr_this_month(report_date),
                    'not_submitted': sdp.child_sdps_not_submitted_randr_this_month(report_date),
                    'not_responded': sdp.child_sdps_not_responded_randr_this_month(report_date),
                    'randrs_sent_to_msd': sdp.child_sdps_processing_sent_to_msd(report_date),
                    'received_delivery': sdp.child_sdps_received_delivery_this_month(report_date)
                   }

    return render_to_response('ilsgateway_dashboard.html',
                              {'sdp': sdp,
                               'language': language,
                               'counts': counts,
                               'groups': groups,
                               'form': form,
                               'select_product_form': select_product_form,
                               'bar_data': bar_data,
                               'bar_ticks': ticks,
                               'form_action': form_action,
                               'facilities_without_primary_contacts': facilities_without_primary_contacts,
                               'randr_inquiry_date': randr_inquiry_date,
                               'delivery_inquiry_date': delivery_inquiry_date,
                               'max_stockout_graph': sdp.child_sdps().count(),
                               'stockouts_by_product': stockouts_by_product,
                               'max_product_count': 12, #limits to 6 products
                               'show_next_month': show_next_month,
                               'next_month_link': next_month_link,
                               'previous_month_link': previous_month_link,
                               'child_sdps_submitting': sdp.child_sdps().filter(delivery_group__name=current_submitting_group(report_date.month) ).count(),
                               'monthly_data': monthly_data,
                               'report_date': report_date,
                               'is_allowed_to_change_location': is_allowed_to_change_location,
                               'breadcrumbs': breadcrumbs
                              },
                              context_instance=RequestContext(request))

@login_required
def message_history(request, facility_id):
    #TODO: restrict to current user's sdp (or by role)
    my_sdp = _get_my_sdp(request)
    facility = ServiceDeliveryPoint.objects.filter(id=facility_id)[0:1].get()    
    breadcrumbs = [[facility.parent.parent.name], 
                   #[facility.parent.name, reverse('ilsgateway.views.dashboard')], 
                   [facility.parent.name],
                   [facility.name, reverse('ilsgateway.views.facilities_detail', args=[facility.id])], 
                   [_('Message History')] ]    
    messages = Message.objects.filter(contact__contactdetail__service_delivery_point=facility_id)
    return render_to_response("message_history.html", 
                              {'messages': messages,
                               "message_history_table": MessageHistoryTable(messages, request=request),
                               'my_sdp': my_sdp,
                               'breadcrumbs': breadcrumbs,
                               'facility': facility}, 
                              context_instance=RequestContext(request))

@login_required
def note_history(request, facility_id):
    facility = ServiceDeliveryPoint.objects.filter(id=facility_id)[0:1].get()    
    breadcrumbs = [[facility.parent.parent.name], 
                   #[facility.parent.name, reverse('ilsgateway.views.dashboard')], 
                   [facility.parent.name],
                   [facility.name, reverse('ilsgateway.views.facilities_detail', args=[facility.id])], 
                   ['Note History'] ]    
    notes = facility.servicedeliverypointnote_set.all().order_by('-created_at')
    return render_to_response("note_history.html", 
                              {'notes': notes,
                               'breadcrumbs': breadcrumbs,
                               'facility': facility}, 
                              context_instance=RequestContext(request))

@login_required
def facilities_index(request, view_type='inventory'):
    month = int(request.GET.get('month', 0))
    year = int(request.GET.get('year', 0))
    order_by = request.GET.get('order_by', 'delivery_group')

    now = datetime.now()
    if month == 0:
        month = now.month 
            
    if year == 0:
        year = now.year 
        
    if year == now.year and month == datetime.now().month:
        show_next_month = False
    else:
        show_next_month = True
    report_date = date(year, month, now.day)
    month_name = report_date.strftime('%B')
    #this can't be right
    next_month_date = report_date + relativedelta(months=+1)
    previous_month_date = report_date + relativedelta(months=-1)
    next_month_link = "/facilities/%s/?month=%d&year=%d" % (view_type, next_month_date.month, next_month_date.year)
    previous_month_link = "/facilities/%s/?month=%d&year=%d" % (view_type, previous_month_date.month, previous_month_date.year) 
    if order_by:
        next_month_link += '&order_by=msd_code'
        previous_month_link += '&order_by=%s' % order_by

    sdp_id = request.session.get('current_sdp_id')
    if sdp_id:
        sdp = ServiceDeliveryPoint.objects.get(id=sdp_id)
    else:
        sdp = _get_my_sdp(request)
    
    if view_type == 'inventory':
        breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], [_('Stock on Hand')] ]
    else:
        breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], [_('Months of Stock')] ]
        
    facilities = Facility.objects.filter(parent_id=sdp.id).order_by(order_by, "name")
    data_table = [] 
    headers = [ ['msd_code', 'MSD Code'],
                ['delivery_group', 'Delivery Group'],
                ['name', 'Facility Name'] ]
    header_row = []
    for header, header_name in headers:
        link='?'
        link += 'month=%d&year=%d' % (report_date.month, report_date.year)
        link += '&order_by=-%s' % header if (order_by == header) else '&order_by=%s' % header                    
        header_row.append({'sorted': 'sorted' if re.search(header, order_by) else None,
                           'direction': 'desc' if re.search('-', order_by) else 'asc',
                           'link': link,
                           'data': header if not header_name else header_name})
    
    for product in Product.objects.all():
        header_row.append({'data': product.name})

    counter = 0
    for facility in facilities:
        row = [{'link': reverse('ilsgateway.views.facilities_detail', args=[facility.id]), 
                'data': facility.msd_code},
               {'data': facility.delivery_group},
               {'data': facility.name}]
        for product in Product.objects.all():
            if view_type=="inventory":
                quantity = facility.stock_on_hand(product.sms_code, report_date)
                cell_class = ''
                if quantity == None:
                    cell_class = 'insufficient_data'
                    quantity = 'No data'
                elif quantity == 0:
                    cell_class = 'zero_count'
                    
                row.append({'data': quantity,
                            'cell_class': cell_class})
            elif view_type == "months_of_stock":
                quantity = facility.months_of_stock(product.sms_code)
                cell_class = ''
                if quantity == None:
                    cell_class = 'insufficient_data'
                    quantity = 'Insufficient data'
                elif quantity == 0:
                    cell_class = 'zero_count'
                elif quantity < settings.MONTHS_OF_STOCK_MIN:
                    cell_class = 'under_min'                    
                elif quantity > settings.MONTHS_OF_STOCK_MAX:                   
                    cell_class = 'exceeds_max'
                row.append({'data': quantity,
                            'cell_class': cell_class})

        data_table.append(row)
        counter += 1
             
    status_table = CurrentMOSTable(facilities,
                                           request,
                                           cell_class=ILSGatewayCell)
        
    return render_to_response("facilities_list.html", 
                              {"breadcrumbs": breadcrumbs,
                               "view_type": view_type,
                               'show_next_month': show_next_month,
                               'next_month_link': next_month_link,
                               'previous_month_link': previous_month_link,
                               'report_date': report_date,                               
                               "status_table": status_table,
                               "data_table": data_table,
                               "header_row": header_row},
                              context_instance=RequestContext(request),)

@login_required
def facilities_ordering(request):
    sdp_id = request.session.get('current_sdp_id')
    if sdp_id:
        sdp = ServiceDeliveryPoint.objects.get(id=sdp_id)
    else:
        sdp = request.user.ilsgatewayuser.service_delivery_point
    breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], [_('Ordering Status')] ]
    facilities = Facility.objects.filter(parent_id=sdp.id).order_by("delivery_group", "name")
    products = Product.objects.all()
    return render_to_response("facilities_ordering.html", 
                              {"facilities": facilities,
                               "products": products,
                               "breadcrumbs": breadcrumbs,
                               "sdp": sdp,
                               "ordering_table": OrderingTable(facilities, request=request, cell_class=ILSGatewayCell),                               
                               },
                              context_instance=RequestContext(request),)

@login_required
def stock_inquiry(request):
    sdp_id = request.session.get('current_sdp_id')
    if sdp_id:
        sdp = ServiceDeliveryPoint.objects.get(id=sdp_id)
    else:
        sdp = request.user.ilsgatewayuser.service_delivery_point
    breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], [_('Ordering Status')] ]
    message = ''
    if request.method == 'POST': 
        form = StockInquiryForm(request.POST) 
        if form.is_valid():
            product = form.cleaned_data['product']
            facilities = form.cleaned_data['facilities']
            districts = form.cleaned_data['districts']
            regions = form.cleaned_data['regions']
#            sdp = ServiceDeliveryPoint.objects.get(msd_code=form.cleaned_data['location'].upper())
#            product = Product.objects.get(product_code=form.cleaned_data['product'])
            for sdps in [facilities, districts, regions]:
                for sdp in sdps:
                    send_test_message = curry(call_router, "httptester", "send")
                    msg_text = 'test send_inquiry_message %s %s' % (sdp.id, product.product_code)
                    send_test_message(identity='11111', text=msg_text)
            message = "Inquiry successfully sent to Facility %s regarding Product %s (%s)" % (sdp.name, product.name, product.product_code)        
            form = StockInquiryForm()                
    else:
            form = StockInquiryForm()                        
   
    return render_to_response("stock_inquiry.html", 
                              {"breadcrumbs": breadcrumbs,
                               "sdp": sdp,
                              'form': form,
                              'message': message
                               },
                              context_instance=RequestContext(request),)

@login_required
def select_location(request):
    sdp = _get_my_sdp(request)
    breadcrumbs = [[sdp.parent.name, ''], [sdp.name, ''], ['Ordering Status'] ]
    sdps = ServiceDeliveryPoint.objects.all().order_by("name")[:20]
    return render_to_response("select_location.html", 
                              {"sdps": sdps,
                               "breadcrumbs": breadcrumbs,
                               "sdp": sdp},
                              context_instance=RequestContext(request),)

@login_required
def facilities_detail(request, facility_id,view_type='inventory'):
    try:
        f = Facility.objects.get(pk=facility_id)
    except Facility.DoesNotExist:
        raise Http404
    products = Product.objects.all()
    breadcrumbs = [[f.parent.parent.name], [f.parent.name, ''], [f.name, ''], [_('Facility Detail')] ]  
    
    product_counts = []
    for product in Product.objects.all():
        if view_type == 'inventory':
            product_counts.append([product.name, f.stock_on_hand(product.sms_code)])
        elif view_type == 'months_of_stock':
            product_counts.append([product.name, f.months_of_stock(product.sms_code)])
    
    if request.method == 'POST': 
        form = NoteForm(request.POST) 
        if form.is_valid():
             n = ServiceDeliveryPointNote()
             n.text = form.cleaned_data['text']
             n.service_delivery_point = f
             n.contact_detail_id = request.user.ilsgatewayuser.id
             n.save()
             form = NoteForm()                
    else:
             form = NoteForm()                        
    notes = f.servicedeliverypointnote_set.order_by('-created_at')[:3]
    contact_groups = []
    contact_groups.append(['Facility', f.contactdetail_set.all().order_by('-role__id')])
    contact_groups.append(['District', f.parent.contactdetail_set.all().order_by('-role__id')])
    contact_groups.append(['Region', f.parent.parent.contactdetail_set.all().order_by('-role__id')])
    return render_to_response('facilities_detail.html', {'facility': f,
                                                         'products': products,
                                                         'view_type': view_type,
                                                         'form': form,
                                                         'breadcrumbs': breadcrumbs,
                                                         'contact_groups': contact_groups,
                                                         'product_counts': product_counts,
                                                         'notes': notes},
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
            base_url='https://www.google.com/accounts/AuthSubRequest'
            scope='https://docs.google.com/feeds/%20https://docs.googleusercontent.com/'
            next_url='http://ilsgateway.com%s' %  request.get_full_path()
            session_val='1'
            target_url="%s?next=%s&scope=%s&session=%s" % (base_url, next_url, scope, session_val)
            return HttpResponseRedirect(target_url)
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

	if not feed.entry:
    		print 'No entries in feed.\n'
  	for entry in feed.entry:
    		print entry.title.text.encode('UTF-8'), entry.GetDocumentType(), entry.resource_id.text

    	# List folders the document is in.
    	for folder in entry.InFolders():
      		print folder.title

        return render_to_response('a.html', {}, context_instance=RequestContext(request))

@gdata_required
def docdownload(request, facility_id):
    """
    Simple example - download google docs document
    """
    if 'token' in request.session:
        #should be able to make this global
        client = gdata.docs.client.DocsClient()
        client.ssl = True  # Force all API requests through HTTPS
        client.http_client.debug = False  # Set to True for debugging HTTP requests
        client.auth_token = gdata.gauth.AuthSubToken(request.session['token'])
        try:
            sdp = ServiceDeliveryPoint.objects.filter(id=facility_id)[0:1].get()
        except:
            raise Http404
        query_string = '/feeds/default/private/full?title=%s&title-exact=false&max-results=100' % sdp.msd_code
        feed = client.GetDocList(uri=query_string)

        most_recent_doc = None

        if not feed.entry:
            link = reverse("ilsgateway.views.facilities_detail", args=[sdp.id])
            return HttpResponse('Sorry, there is no recent R&R for this facility. Click <a href="%s">here to return to %s facility detail.</a>.' % (link, sdp.name))
        else:
            for entry in feed.entry:
                if not most_recent_doc:
                        most_recent_doc = entry
                else:
                    new_date = iso8601.parse_date(entry.updated.text)
                    old_date = iso8601.parse_date(most_recent_doc.updated.text)
                    if new_date > old_date:
                        most_recent_doc = entry

        exportFormat = '&exportFormat=pdf'
        content = client.GetFileContent(uri=most_recent_doc.content.src + exportFormat)
    response = HttpResponse(content)
    response['content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename=%s' % most_recent_doc.title.text
    return response

def _get_my_sdp(request):    
    contact_detail = ContactDetail.objects.get(user=request.user.ilsgatewayuser.id)
    my_sdp = request.user.ilsgatewayuser.service_delivery_point
    return my_sdp

def _get_current_sdp(request):
    if not request.session.get('current_sdp_id'):
        my_sdp = _get_my_sdp(request)
        if my_sdp.service_delivery_point_type.name == "MOHSW":
            sdp = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name="DISTRICT")[0]
            request.session['current_sdp_id'] = sdp.id
        elif my_sdp.service_delivery_point_type.name == "REGION":
            #TODO: hacky, no real region views so we set the default to be the first child
            sdp = my_sdp.child_sdps()[0]
            request.session['current_sdp_id'] = sdp.id       
        else:
            sdp = my_sdp
            request.session['current_sdp_id'] = sdp.id
    else:
        sdp = ServiceDeliveryPoint.objects.get(id=request.session.get('current_sdp_id'))
    return sdp

def _get_role(request):
    return request.user.ilsgatewayuser.role
    

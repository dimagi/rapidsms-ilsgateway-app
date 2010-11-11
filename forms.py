#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms
from ilsgateway.models import ContactDetail, ServiceDeliveryPoint, ContactRole
from rapidsms.models import Backend, Connection
from rapidsms.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q

class ContactDetailForm(forms.ModelForm):
    name = forms.CharField()
    primary = forms.BooleanField(initial=True, required=False)
    phone = forms.CharField()
    class Meta:
        model = ContactDetail
        widgets = {"Language": forms.Select(choices=( ('sw', 'Swahili'), ('en', 'English'), ) ),}
        exclude = ("user",)
    def __init__(self, service_delivery_point=None, cd=None, **kwargs):
        super(ContactDetailForm, self).__init__(**kwargs)
        self.fields['role'].label = _("Role")
        self.fields['language'].label = _("Language")
        self.fields['email'].label = _("Email")
        self.fields['name'].label = _("Name")
        self.fields['primary'].label = _("Primary")
        self.fields['phone'].label = _("Phone")
        self.fields['service_delivery_point'].label = _("Service Delivery Point")
        
        #hardcoded permissions, unfortunately    
        if cd:
            if cd.role.id in [2,4]:
                self.fields['role'].queryset = ContactRole.objects.filter(pk=1)
                self.fields['service_delivery_point'].queryset = service_delivery_point.child_sdps().order_by("name")
            elif cd.role.id in [3]:
                self.fields['role'].queryset = ContactRole.objects.filter(id__in=[1,2,4])
                self.fields['service_delivery_point'].queryset = ServiceDeliveryPoint.objects.filter(Q(parent_id=service_delivery_point.id) |
                                                                                                     Q(id=service_delivery_point.id))
            elif cd.role.id in [5,6]:
                self.fields['role'].queryset = ContactRole.objects.filter(id__in=[1,2,3,4,5,6])
                self.fields['service_delivery_point'].queryset = ServiceDeliveryPoint.objects.filter(Q(parent_id=service_delivery_point.id) |
                                                                                                     Q(id=service_delivery_point.id) |
                                                                                                     Q(id=service_delivery_point.parent_id))

        if kwargs.has_key('instance'):
            if kwargs['instance']:
                instance = kwargs['instance']
                self.initial['phone'] = instance.phone

    def save(self, commit=True):
        model = super(ContactDetailForm, self).save(commit=False)
        if commit:
            model.save()
            conn = model.default_connection 
            if not conn:
                if settings.DEFAULT_BACKEND:
                    backend = Backend.objects.get(name=settings.DEFAULT_BACKEND)
                else:
                    backend = Backend.objects.all()[0]
                conn = Connection(backend=backend,
                                  contact=model.contact_ptr)
            conn.identity = self.cleaned_data['phone']
            conn.save()
            print conn
        return model            

class NoteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea,label="", help_text="", max_length=500)
    
class SelectLocationForm(forms.Form):
    location = forms.ChoiceField()    

    def __init__(self, service_delivery_point=None, **kwargs):
        super(SelectLocationForm, self).__init__(**kwargs)
        if service_delivery_point:
            if service_delivery_point.service_delivery_point_type.name == "MOHSW":
                self.fields['location'].choices = ServiceDeliveryPoint.objects.filter(service_delivery_point_type__name="DISTRICT").order_by("name").values_list('id', 'name')
            else:
                self.fields['location'].choices = ServiceDeliveryPoint.objects.filter(parent_id=service_delivery_point.id).order_by("name").values_list('id', 'name')
    
    
    
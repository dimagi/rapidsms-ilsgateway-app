#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms
from ilsgateway.models import ContactDetail, ServiceDeliveryPoint
from rapidsms.models import Backend, Connection
from rapidsms.conf import settings

class ContactDetailForm(forms.ModelForm):
    primary = forms.BooleanField(initial=True, required=False)
    phone = forms.CharField()
    class Meta:
        model = ContactDetail
        widgets = {'language': forms.Select(choices=( ('sw', 'Swahili'), ('en', 'English'), ) ),}
        exclude = ("user",)
    def __init__(self, service_delivery_point=None, **kwargs):
        super(ContactDetailForm, self).__init__(**kwargs)
        if service_delivery_point:
            self.fields['service_delivery_point'].queryset = service_delivery_point.child_sdps().order_by("name")
 
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
    
    
    
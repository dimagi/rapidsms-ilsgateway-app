#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms
from ilsgateway.models import ContactDetail, ServiceDeliveryPoint

class ContactDetailForm(forms.ModelForm):
    primary = forms.BooleanField(initial=True, required=False)
    class Meta:
        model = ContactDetail
        widgets = {'language': forms.Select(choices=( ('sw', 'Swahili'), ('en', 'English'), ) ),}
        exclude = ("user",)
    def __init__(self, service_delivery_point=None, **kwargs):
        super(ContactDetailForm, self).__init__(**kwargs)
        if service_delivery_point:
            self.fields['service_delivery_point'].queryset = service_delivery_point.child_sdps().order_by("name")

class NoteForm(forms.Form):
    text = forms.CharField()
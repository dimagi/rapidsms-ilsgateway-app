#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms
from ilsgateway.models import ContactDetail, ServiceDeliveryPoint

class ContactDetailForm(forms.ModelForm):
    class Meta:
        model = ContactDetail
        exclude = ("user",)
    def __init__(self, service_delivery_point=None, **kwargs):
        super(ContactDetailForm, self).__init__(**kwargs)
        if service_delivery_point:
            self.fields['service_delivery_point'].queryset = ServiceDeliveryPoint.objects.filter(parent_service_delivery_point=service_delivery_point).order_by("name")

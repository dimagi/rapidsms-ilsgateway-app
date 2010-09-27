#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from djtables import Table, Column
from django.core.urlresolvers import reverse

def _edit_link(cell):
    return reverse(
        "registration_edit",
        args=[cell.row.pk])

class ContactDetailTable(Table):
    name = Column(link=_edit_link)
    language = Column()
    role = Column()
    service_delivery_point = Column()
    primary = Column()

    class Meta:
        order_by = 'service_delivery_point__name'

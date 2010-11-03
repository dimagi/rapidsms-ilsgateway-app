#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from djtables import Table, Column
from djtables.column import DateColumn
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

def _edit_link(cell):
    return reverse(
        "registration_edit",
        args=[cell.row.pk])

class ContactDetailTable(Table):
    name = Column(link=_edit_link)
    language = Column()
    #role = Column()
    service_delivery_point = Column()
    primary = Column()

    class Meta:
        order_by = 'service_delivery_point__name'

def _get_role(cell):
    return _(cell.object.contact.contactdetail.role.name)

def _get_direction(cell):
    if  cell.object.direction == "I":
        return _("In")
    else:
        return _("Out")
    
class MessageHistoryTable(Table):
    contact = Column(value=lambda u: u.object.contact.name)
    direction = Column(value=_get_direction)
    role = Column(value=_get_role, sortable=False)
    phone = Column(value=lambda u: _(u.object.contact.contactdetail.phone()), sortable=False)
    date = DateColumn(format="H:m:s d/m/Y")
    text = Column()
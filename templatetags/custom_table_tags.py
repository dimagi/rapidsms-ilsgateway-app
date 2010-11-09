from django import template
register = template.Library()
from djtables.column import WrappedColumn

@register.inclusion_tag("djtables/translated_djtables_head.html")
def translated_table_head(table):
    return {
        "columns": [
            WrappedColumn(table, column)
            for column in table.columns ] }


from django import template
register = template.Library()
from djtables.column import WrappedColumn

@register.inclusion_tag("djtables/ilsgateway_djtables_head.html")
def message_history_table_head(table):
    return {
        "columns": [
            WrappedColumn(table, column)
            for column in table.columns ] }


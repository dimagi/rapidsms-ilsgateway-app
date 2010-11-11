from django import template
register = template.Library()
from djtables.column import WrappedColumn

@register.inclusion_tag("djtables/translated_djtables_head.html")
def translated_table_head(table):
    return {
        "columns": [
            WrappedColumn(table, column)
            for column in table.columns ] }

@register.inclusion_tag("djtables/stock_table_body.html")
def stock_table_body(table):
    return {
        "rows": table.rows,
        "unicode_zero": u"0",
        "unicode_none": u"None",
        "num_columns": len(table.columns) }

@register.inclusion_tag("djtables/ordering_table_body.html")
def ordering_table_body(table):
    return {
        "rows": table.rows,
        "num_columns": len(table.columns) }
    
def underscoretospaces(value):
    ""
    return value.replace('_', ' ')

register.filter('underscoretospaces',underscoretospaces)
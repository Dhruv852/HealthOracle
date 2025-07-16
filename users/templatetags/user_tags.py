from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add a CSS class to the specified form field.
    
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='split')
def split(value, delimiter=None):
    """
    Split a string into a list using the specified delimiter.
    
    Usage: {{ text|split:delimiter }}
    """
    if delimiter is None:
        return value.split()
    return value.split(delimiter)
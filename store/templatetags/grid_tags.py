from django import template
from django.utils.html import format_html


register = template.Library()

@register.simple_tag
def containerfluid(extra_classes=""):
    return format_html('<div class="container-fluid {}">', extra_classes)

@register.simple_tag
def container(extra_classes=""):
    return format_html('<div class="container {}">', extra_classes)

@register.simple_tag
def endcontainer():
    return format_html("</div>")

@register.simple_tag
def row(extra_classes=""):
    return format_html('<div class="row {}">', extra_classes)

@register.simple_tag
def endrow():
    return format_html("</div>")

@register.simple_tag
def col(extra_classes=""):
    return format_html('<div class="col {}">', extra_classes)

@register.simple_tag
def endcol():
    return format_html("</div>")
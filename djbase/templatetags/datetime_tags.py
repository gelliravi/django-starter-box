import datetime

from django import template, forms
from django.utils.translation import ugettext_lazy as _l

register = template.Library()

_DAYS = [_l('Mon'), _l('Tue'), _l('Wed'), _l('Thu'), _l('Fri'), _l('Sat'), _l('Sun')]

@register.filter
def day_of_week(value):
    return _DAYS[value]

@register.filter
def time_from_24h(value):
    return datetime.time(int(value // 100), value % 100, 0)

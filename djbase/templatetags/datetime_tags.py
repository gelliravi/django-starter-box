import datetime

from django import template, forms
from django.utils.translation import ugettext_lazy as _

register = template.Library()

_DAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]

@register.filter
def day_of_week(value):
    return _DAYS[value]

@register.filter
def time_from_24h(value):
    return datetime.time(int(value // 100), value % 100, 0)

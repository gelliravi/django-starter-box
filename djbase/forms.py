from __future__ import unicode_literals

from datetime import datetime

from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from .utils import parse_iso_datetime

class ISODateTimeField(forms.Field):
    """Input is either datetime objects or ISO formatted strings, and
    output is datetime object.

    The value passed in must be a Python string containing a datetime in ISO
    format, or datetime objects. This is generally not used for human input.
    """

    default_error_messages = {
        'invalid': _('Invalid ISO date')
    }

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, six.text_type):
            value = value.strip()

            if value == '':
                return None 

            try:
                return parse_iso_datetime(value)
            except Exception:
                pass

        raise ValidationError(self.error_messages['invalid'], code='invalid')

class TrimmedCharField(forms.CharField):
    """Exactly the same as forms.CharField except that it trims its input.
    """

    def to_python(self, value):
        # CharField always return a string, so we can safely call strip()
        value = super(TrimmedCharField, self).to_python(value).strip()
        return value 

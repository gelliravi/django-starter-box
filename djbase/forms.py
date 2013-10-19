from django import forms
from django.forms import ValidationError

from .utils import parse_iso_datetime

from datetime import datetime

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

        if isinstance(value, basestring):
            value = value.strip()

            if value == '':
                return None 

            try:
                return parse_iso_datetime(value)
            except Exception:
                pass

        raise ValidationError(self.error_messages['invalid'], code='invalid')


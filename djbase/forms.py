from __future__ import unicode_literals

from django import forms
from django.forms import ValidationError
from django.forms.widgets import TextInput, PasswordInput
from django.utils.translation import ugettext_lazy as _l

from .utils import parse_iso_datetime

from datetime import datetime

class ISODateTimeField(forms.Field):
    """Input is either datetime objects or ISO formatted strings, and
    output is datetime object.

    The value passed in must be a Python string containing a datetime in ISO
    format, or datetime objects. This is generally not used for human input.
    """

    default_error_messages = {
        'invalid': _l('Invalid ISO date')
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

class FixedCharField(forms.CharField):
    """
    Fixed-length character field. Length is measured in terms of bytes,
    specifically the number of bytes needed for the string's UTF-8 encoding.
    """

    default_error_messages = {
        'wrong_length': _l('Please ensure this value has exactly %(set_length)d characters (it has %(value_length)d).'),
    }

    def __init__(self, max_length, *args, **kwargs):
        super(FixedCharField, self).__init__(max_length=max_length, min_length=max_length, *args, **kwargs)

    def validate(self, value):
        # we standardize to byte length.
        value_length = len(value.encode('utf-8'))
        if value_length != self.max_length:
            raise ValidationError(self.error_messages['wrong_length'], code='wrong_length', params={'set_length': self.max_length, 'value_length': value_length})

        return super(FixedCharField, self).validate(value)
        
    def widget_attrs(self, widget):
        attrs = super(FixedCharField, self).widget_attrs(widget)
        if isinstance(widget, (TextInput, PasswordInput)):
            # The HTML attribute is maxlength, not max_length.
            attrs.update({'maxlength': str(self.max_length)})
        return attrs

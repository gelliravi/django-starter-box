# need this since this module's name clashes with the global json
from __future__ import absolute_import 
from __future__ import unicode_literals

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise, curry
from django.utils.encoding import force_text

import json

class Encoder(DjangoJSONEncoder):
    """JSON encoder that encodes datetime and date as ISO format.
    
    This is needed as simplejson and json don't encode dates.
    The ISO format is supported by json2.js.
    See "Date Time String Format" in the ECMA-262 specification.
    See https://github.com/django/django/blob/master/django/core/serializers/json.py
    """

    # simplejson 2.2.0+ will pass these extra args to __init__ which 
    # aren't accepted by DjangoJSONEncoder because it is based on json not
    # simplejson:
    # - use_decimal
    # - namedtuple_as_object
    # - tuple_as_array
    def __init__(self, *args, **kwargs):
        self._parent = super(Encoder, self)    
        self._parent.__init__(*args, **kwargs)
    
    def default(self, obj):        
        # handle lazy translation strings
        if isinstance(obj, Promise):
            return force_text(obj)

        if hasattr(obj, 'to_json'):
            return obj.to_json()

        return self._parent.default(obj)

encode = curry(
    json.dumps, 
    separators=(',', ':'),  # most compact JSON output
    cls=Encoder             # encodes datetime's
)


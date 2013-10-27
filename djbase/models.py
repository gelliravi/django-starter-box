from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _l

# for Python 2 & 3 compat
from django.utils.six import with_metaclass
from django.utils import six

from .forms import TrimmedCharField

# cPickle for speed
try:
    import cPickle as pickle
except ImportError:
    import pickle

class BaseModel(models.Model):
    """A mixin providing some useful generic methods.
    """

    @classmethod
    def field(cls, name):
        return cls._meta.get_field(name)

    class Meta:
        abstract = True

# Subclass SubfieldBase to ensure to_python() is called everytime value is set.
class PickleField(with_metaclass(models.SubfieldBase, models.TextField)):
    """Represents a field that stores any arbitrary Python object 
    (except a string). If you want to store a string, use a regular TextField.

    The Python object is serialized using Pickle and stored as ASCII.
    DO NOT assign a string to this field. The reason being to_python()
    is always called whenever a value is assigned, and since a pickled value
    is also a string, there is no way to distinguish between an unpickled
    string and a pickled value (except to try-catch any Pickle decoding error).
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        
        # pickle the default value
        def_val = kwargs.get('default', None)
        kwargs['default'] = pickle.dumps(def_val)

        super(PickleField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, six.text_type):
            # Django probably converts the value to unicode,
            # so we have to convert it back.
            return pickle.loads(value.encode('ascii'))
        elif isinstance(value, bytes):
            return pickle.loads(value)

        return value 

    def get_prep_value(self, value):
        # None is treated as null in database
        if value is None:
            return value 

        return pickle.dumps(value)

class FixedCharField(with_metaclass(models.SubfieldBase, models.CharField)):
    description = _l('String (exactly %(max_length)s)')

    def __init__(self, max_length, *args, **kwargs):
        self._parent = super(FixedCharField, self)
        self._parent.__init__(max_length=max_length, *args, **kwargs)

    def db_type(self, connection):
        engine = connection.settings_dict['ENGINE']

        if engine == 'django.db.backends.mysql' or \
           engine == 'django.db.backends.postgresql' or \
           engine == 'django.db.backends.sqlite3':
            return 'char(%s)' % (self.max_length)
        
        elif engine == 'django.db.backends.oracle':
            return 'nchar(%s)' % (self.max_length)

        return self._parent.db_type(connection)

    def to_python(self, value):
        value = self._parent.to_python(value)

        if value is None:
            return value 

        return value.strip()

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', TrimmedCharField)
        kwargs.setdefault('max_length', self.max_length)
        return self._parent.formfield(**kwargs)

    # I guess this is necessary when there are custom args in the __init__
    # method.
    def south_field_triple(self):
        "Returns a suitable description of this field for South."

        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        
        field_class = self.__class__.__module__ + "." + self.__class__.__name__
        args, kwargs = introspector(self)
        
        # That's our definition!
        return (field_class, args, kwargs)

# South support; see http://south.aeracode.org/docs/tutorial/part4.html#simple-inheritance
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^djbase\.models\.FixedCharField"])
    add_introspection_rules([], [r"^djbase\.models\.PickleField"])

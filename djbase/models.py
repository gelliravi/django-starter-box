from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _l

# for Python 2 & 3 compat
from django.utils.six import with_metaclass
from django.utils import six

from . import forms

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
    (except a string). 

    The Python object is serialized using Pickle and stored as ASCII.
    DO NOT assign a string to this field. (A string inside a structure such as
    tuple/list/dict is OK.) The reason is that to_python()
    is always called whenever a value is assigned, and since a pickled value
    is also a string, there is no way to distinguish between an unpickled
    string and a pickled value (except to try-catch any Pickle decoding error).
    If you want to store a string, use a regular TextField.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)

        # Shouldn't impose a max_length as we don't know how big the pickled
        # value is going to be.
        kwargs.pop('max_length', None)

        def_val = kwargs.get('default', None)
            
        if hasattr(def_val, '__call__'):
            def_val = def_val()

        # must pickle the default value as models.Field.get_default() will
        # convert it into a string, resulting in a unpickling error.
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

class TrimmedTextField(with_metaclass(models.SubfieldBase, models.TextField)):
    """ Exactly the same as models.TextField, except that it trims the input.
    """

    def to_python(self, value):
        value = self._parent.to_python(value)

        if value is None:
            return value 

        return value.strip()

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.TrimmedTextField)
        kwargs.setdefault('max_length', self.max_length)
        return self._parent.formfield(**kwargs)

class TrimmedCharField(with_metaclass(models.SubfieldBase, models.CharField)):
    """ Exactly the same as models.CharField, except that it trims the input.
    """

    def to_python(self, value):
        value = self._parent.to_python(value)

        if value is None:
            return value 

        return value.strip()

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.TrimmedCharField)
        kwargs.setdefault('max_length', self.max_length)
        return self._parent.formfield(**kwargs)

class FixedCharField(with_metaclass(models.SubfieldBase, models.CharField)):
    """Represents a fixed-length char model field. 

    In practice, it accepts any length up to max_length, 
    but the underlying database column will be of fixed-length char type.
    The database may pad the value, but this field will trim the value 
    when retrieved from the database.
    """

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
        kwargs.setdefault('form_class', forms.TrimmedCharField)
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
    add_introspection_rules([], [r"^djbase\.models\.TrimmedTextField"])
    add_introspection_rules([], [r"^djbase\.models\.TrimmedCharField"])
    add_introspection_rules([], [r"^djbase\.models\.FixedCharField"])
    add_introspection_rules([], [r"^djbase\.models\.PickleField"])

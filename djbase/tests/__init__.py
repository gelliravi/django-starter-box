from __future__ import unicode_literals

from django.db import models 
from djbase.models import PickleField, FixedCharField

# Must put models here so they can be synced during test.

class PickleFieldTestModel(models.Model):
    optional = PickleField(null=True, blank=True, default=(1,2))
    required = PickleField(null=False, blank=False) # default is None
    
class FixedCharFieldTestModel(models.Model):
    optional = FixedCharField(null=True, blank=True, max_length=10, default='a')
    required = FixedCharField(null=False, blank=False, max_length=20)

from .models import *
from .utils import *

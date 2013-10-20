from __future__ import unicode_literals

from django.db import models 
from djbase.models import PickleField

class PickleModelTest(models.Model):
    p = PickleField()
    p2 = PickleField(default=(1,2))


from .models import *
from .utils import *

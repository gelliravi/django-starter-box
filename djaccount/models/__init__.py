from __future__ import unicode_literals

from django.db import IntegrityError, models, DatabaseError
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import pgettext_lazy as _pl, ugettext_lazy as _l
from djbase.models import FixedCharField, BaseModel

import importlib 
import sys 

_mgrs = importlib.import_module('.managers', 'djaccount.models')

# This file gets loaded before the override_settings take effect,
# and so we cannot override AUTH_USER_MODEL.
if 'test' in sys.argv:
    _USER_MODEL = 'djaccount.Account'
else:
    _USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', None) or \
                  'auth.User'

# See how to customize:
# https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#auth-custom-user
# https://github.com/django/django/blob/1.5.4/django/contrib/auth/models.py
class AbstractAccount(AbstractBaseUser, PermissionsMixin, BaseModel):
    class Meta:
        abstract = True 

    MALE        = 'm'
    FEMALE      = 'f'

    GENDER_CHOICES  = (
        (MALE,           _l('Male')),
        (FEMALE,         _l('Female')),
    )

    INVALID_TIMEZONE = 32000

    email           = models.EmailField(max_length=75, unique=True, db_index=True)
    first_name      = models.CharField(max_length=50)
    middle_name     = models.CharField(max_length=50, blank=True, default='')
    last_name       = models.CharField(max_length=50, blank=True, default='')

    gender          = FixedCharField(max_length=1, blank=True, default='', choices=GENDER_CHOICES)
    
    timezone        = models.PositiveSmallIntegerField(default=INVALID_TIMEZONE)
    """UTC offset in minutes"""

    locale          = FixedCharField(max_length=5, blank=True, default='')
    """Example: en_US"""

    is_staff        = models.BooleanField()

    is_active       = models.BooleanField()
    """Whether the email address is verified."""

    is_first_name   = models.BooleanField(default=True)
    """Whether first name comes first."""

    created         = models.DateTimeField(auto_now_add=True)

    objects         = _mgrs.AbstractAccountManager()

    REQUIRED_FIELDS = ['first_name']    
    USERNAME_FIELD  = 'email'

    def get_full_name(self):
        if self.last_name:
            if self.is_first_name:
                return self.first_name + ' ' + self.last_name
            else:
                return self.last_name + ' ' + self.first_name
        else:
            return self.first_name 
                
    def get_short_name(self):
        return self.first_name

    def to_json(self):
        """
        Returns a dict representing this Account. 
        
        A limited set of fields is returned as this will be exposed publicly.
        You may override this method to return any fields you want.
        """

        return {
            'id'        : self.id,
            'firstName' : self.first_name,
            'lastName'  : self.last_name,
            'shortName' : self.get_short_name(),
            'fullName'  : self.get_full_name(),
        }

    def to_json_full(self):    
        """
        Returns a dict representing this Account.

        You may override this if you wish.
        """

        return {
            'id'        : self.id,
            'firstName' : self.first_name,
            'lastName'  : self.last_name,
            'shortName' : self.get_short_name(),
            'fullName'  : self.get_full_name(),
            'email'     : self.email,
            'lastLogin' : self.last_login,
        }

    def __unicode__(self):
        return self.email

if _USER_MODEL == 'djaccount.Account':
    class Account(AbstractAccount):
        pass 

class AccountPasswordReset(BaseModel):
    hash        = FixedCharField(max_length=32, primary_key=True)
    account     = models.ForeignKey(_USER_MODEL, unique=True)
    is_done     = models.BooleanField(default=False)
    created     = models.DateTimeField(auto_now_add=True)

    changed     = models.DateTimeField(auto_now=True)
    """ Valid only when is_done is True. """

class AccountExternal(BaseModel):
    account     = models.ForeignKey(_USER_MODEL, db_index=False)
    service     = models.PositiveSmallIntegerField()
    service_id  = models.CharField(max_length=32)
    created     = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (
            ('service', 'service_id'),
            ('account', 'service'),
        )

class AccountExternalFriends(BaseModel):
    account     = models.ForeignKey(_USER_MODEL, db_index=False)
    service     = models.PositiveSmallIntegerField()
    friend_id   = models.CharField(max_length=32)

    class Meta:
        unique_together = (
            ('account', 'service', 'friend_id')
        )

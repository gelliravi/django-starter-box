from __future__ import unicode_literals

import hashlib
import importlib 
import datetime
import uuid

from django.db import IntegrityError, models, DatabaseError, transaction
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from django.utils import timezone

from djaccount.exceptions import *
from djaccount.conf import settings as app_settings

from djbase.utils.mock import is_test 

if is_test():
    from djbase.utils.mock import facebook 
else:
    import facebook

_models = importlib.import_module('djaccount.models')

class AbstractAccountManager(BaseUserManager):
    SERVICE_FB      = 1

    @classmethod
    def normalize_email(cls, email):
        """ Whether to lowercase entire email based on 
        ACCOUNT_LOWER_EMAIL setting. """

        if app_settings.ACCOUNT_LOWER_EMAIL:
            email = email or '' # follow BaseUserManager's behavior
            return email.lower()
        else:
            return BaseUserManager.normalize_email(email)

    def change_email(self, account, email):
        """Changes the email of an account and resets the verification status.
        
        This will NOT send a verification email.
        On error, object state is unaffected.
        
        :type  account: AbstractAccount 

        :returns:   void
        :raises:    AccountError
        """

        email = self.normalize_email(email)

        old_email       = account.email 
        old_is_active   = account.is_active

        account.email       = email
        account.is_active   = False 
        ok  = False

        try:
            account.save(update_fields=('email', 'is_active'))
            ok = True
        except IntegrityError as e:
            raise AccountEmailTakenError(cause=e)
        finally:
            if not ok:
                account.email       = old_email
                account.is_active   = old_is_active

    def calc_verify_code(self, account):
        """Gets the email verification code.

        :type account: AbstractAccount

        :returns:   str -- code.
        """

        created_str = account.created.strftime('%Y-%m-%d_%H:%M:%S')

        m = hashlib.sha1()
        m.update('%s|%s|%s|%s' % (account.id, account.email, created_str, app_settings.ACCOUNT_SECRET_KEY))

        code = m.hexdigest().lower()
        return code 

    def do_verify(self, account, code):
        """Checks verification code and sets verification status.
        
        On error, object state is unaffected.
        
        :returns:   bool -- success or not.
        :raises:    DatabaseError
        """

        real_code = self.calc_verify_code(account=account)

        if real_code != code:
            return False

        # This will not trigger the pre_save signal.    
        ok = self.filter(pk=account.pk, email=account.email).update(is_active=True) > 0
        if ok:
            account.is_active = True 

        return ok

    def _set_login(self, account, request, remember):        
        if remember:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE) 
        else:
            # 0 means expire on browser exit
            request.session.set_expiry(0)

        auth_login(request, account)
        
    def login_external(self, service, service_id, request, remember=True):
        """
        Logins a user passwordless-ly with an external account.

        Any current session data is retained.
        This does not require the user's email to be verified beforehand.
        Warning: since this is a passwordless login, the service and service_id
        must have been authenticated somewhere else. It is recommended that
        all code paths that involve calling this method come from a POST request
        which has CSRF protection.

        :param  request:    request.user will be set accordingly.
        :param  service:    AbstractAccountManager.SERVICE_* 
        :param  service_id: ID of the external service. For example, Facebook user ID.
        :param  remember:   Whether to remember the login session for some time.
        
        :raises:    AccountMissingError 
        :returns:   AbstractAccount
        """

        account = authenticate(username=(service, service_id), password=None)
        if account:
            self._set_login(account=account, request=request, remember=remember)
        else:
            raise AccountMissingError()

        return account 

    def login(self, email, password, request, remember=True):
        """
        Logins a user.

        Any current session data is retained.
        This does not require the user's email to be verified beforehand.

        :param  request:    request.user will be set accordingly.
        :param  remember:   Whether to remember the login session for some time.
        
        :raises:    AccountLoginError, AccountMissingError, AccountNoPasswordError
        :returns:   AbstractAccount
        """

        email = self.normalize_email(email)
        account = authenticate(username=email, password=password)
        if account:
            self._set_login(account=account, request=request, remember=remember)
        else:
            # Now need to find out the exact login error reason.
            try:
                account = self.get(email=email)
            except self.model.DoesNotExist as e: 
                raise AccountMissingError(cause=e)

            if account.has_usable_password():
                raise AccountLoginError()
            else:
                # if the user is created thru an external auth system,
                # then he cannot login using the regular method unless he has a password.
                raise AccountNoPasswordError()

        return account

    def logout(self, request):
        """Logs out the user and destroys all session data.

        :returns:   void 
        """

        auth_logout(request)

    def link_external(self, account, service, service_id):
        """
        Links an external account to an account. 

        :param account: Warning: This must have been already logined.

        :returns:   AccountExternal
        :raises:    AccountExternalTakenError
        """

        try:
            ext = _models.AccountExternal.objects.select_related().get(service=service, service_id=service_id)
        except _models.AccountExternal.DoesNotExist: 
            pass 
        else:
            # Already linked
            if ext.account.id == account.id: 
                return ext 
            else: 
                raise AccountExternalTakenError()

        try:
            ext = _models.AccountExternal.objects.create(account=account, service=service,service_id=service_id)
        except IntegrityError as e:
            raise AccountExternalTakenError(cause=e)
        
        return ext

    def create_external_user(self, email, first_name, service, service_id):
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        # Assume external account's email is not validated, for example,
        # for Facebook, you can register using someone else's email.
        account = self.model(email=email, first_name=first_name, is_staff=False, is_active=False)
        account.set_unusable_password()

        with transaction.commit_on_success():
            try:
                account.save() 
            except IntegrityError as e:
                # email is already taken, then we try to link the external account
                # Don't reset current user's password.
                account = self.get(email=email)
                if not account.is_active:
                    # email is not verified: unsafe to link 
                    raise AccountExternalSameEmailError(cause=e)  
            
            ext = _models.AccountExternal.objects.create(account=account, service=service,service_id=service_id)
            
        return ext

    def create_user(self, email, first_name, password):
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        # active=False means must validate email first
        account = self.model(email=email, first_name=first_name, is_staff=False, is_active=False)
        account.set_password(password)

        try:
            account.save() 
        except IntegrityError as e:
            raise AccountEmailTakenError(cause=e)

        return account 

    def create_superuser(self, email, first_name, password):
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        account = self.model(email=email, first_name=first_name, is_staff=True, is_active=True, is_superuser = True)
        account.set_password(password)

        try:
            account.save() 
        except IntegrityError as e:
            raise AccountEmailTakenError(cause=e)

        return account

    def fb_login(self, request, app_id, app_secret):
        cur_user = request.user
        cookies  = request.COOKIES 

        if cur_user.is_authenticated():
            ext = self.fb_link(account=cur_user, cookies=cookies, app_id=app_id, app_secret=app_secret)
        else:
            ext = self.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)
            self.login_external(request=request, service=ext.service, service_id=ext.service_id)
        
        return ext 

    def fb_link(self, account, cookies, app_id, app_secret):
        """Link a Facebook account with an existing account."""

        user        = facebook.get_user_from_cookie(cookies, app_id, app_secret)
        if not user:
            raise AccountNoCookieError() 

        service     = self.SERVICE_FB
        service_id  = user['uid']

        ext = self.link_external(account=account, service=service, service_id=service_id)

        graph       = facebook.GraphAPI(user["access_token"])  
        profile     = self._fb_load_profile(graph=graph)
        self._fb_update_account(account=ext.account, profile=profile)

        return ext 

    def _fb_load_profile(self, graph):
        profile     = graph.get_object("me", fields="friends.id,email,first_name,middle_name,last_name,gender,name,timezone,locale,age_range")
        return profile

    def _fb_update_account(self, account, profile):
        service     = self.SERVICE_FB
        first_name  = profile['first_name']
        middle_name = profile.get('middle_name', None)
        last_name   = profile.get('last_name', None)
        name        = profile['name']
        gender      = profile['gender']
        timezone    = profile.get('timezone', None)
        locale      = profile.get('locale', None)
        age_range   = profile.get('age_range', None)
            
        #
        # Populate account with profile info on first link to fb
        #
        if gender == 'male':
            gender = self.model.MALE
        elif gender == 'female':
            gender = self.model.FEMALE
        else:
            gender = None 

        update_fields       = []
        if not account.gender and gender:
            account.gender      = gender 
            update_fields.append('gender')

        if not account.middle_name and middle_name:
            account.middle_name = middle_name 
            update_fields.append('middle_name')

        account.is_first_name = name.startswith(first_name) 
        update_fields.append('is_first_name')    

        if not account.last_name and last_name:
            account.last_name   = last_name 
            update_fields.append('last_name')

        if account.timezone == self.model.INVALID_TIMEZONE and not timezone is None:
            account.timezone = round(timezone * 60) # convert to mins
            update_fields.append('timezone')

        if not account.locale and locale:
            account.locale = locale 
            update_fields.append('locale')

        """
        Don't support this for now.
        if age_range:
            if account.age_range_min == 0 and 'min' in age_range:
                account.age_range_min = age_range['min']
                update_fields.append('age_range_min')

            if account.age_range_max == 0 and 'max' in age_range:
                account.age_range_max = age_range['max']
                update_fields.append('age_range_max')
        """

        if len(update_fields):
            account.save(force_update=True, update_fields=update_fields)
        
        friends = profile['friends']['data']
        friend_objs = []
        for f in friends: 
            friend_objs.append(_models.AccountExternalFriends(account=account, service=service, friend_id=f['id']))

            if len(friend_objs)==100:
                _models.AccountExternalFriends.objects.bulk_create(friend_objs)
                friend_objs = []

        if len(friend_objs):
            _models.AccountExternalFriends.objects.bulk_create(friend_objs)
        
    def fb_load_or_create(self, cookies, app_id, app_secret):
        """Gets or create a new account based on Facebook login."""

        user        = facebook.get_user_from_cookie(cookies, app_id, app_secret)
        if not user:
            raise AccountNoCookieError() 

        service     = self.SERVICE_FB
        service_id  = user['uid']

        try:
            ext = _models.AccountExternal.objects.select_related().get(service=service, service_id=service_id)
        except _models.AccountExternal.DoesNotExist:
            ext = None 
        else: 
            return ext 

        graph       = facebook.GraphAPI(user["access_token"])  
        profile     = self._fb_load_profile(graph=graph)
        first_name  = profile['first_name']
        email       = profile.get('email', None)
            
        if email:
            email = self.normalize_email(email)
        else:
            raise AccountExternalNoEmailError() 

        ext = self.create_external_user(email=email, first_name=first_name, service=service, service_id=service_id)
        account = ext.account 
        
        # Populate on first link.
        self._fb_update_account(account=account, profile=profile)
        return ext

    def load_external(self, account):
        exts = {}
        rows = _models.AccountExternal.objects.filter(account=account)

        for r in rows:
            service = r.service 
            exts[service] = {
                'id'    : r.service_id
            }

        return exts

    def _calc_password_reset_hashed_token(self, token):
        m = hashlib.sha1()
        s = '%s_%s' % (token, app_settings.ACCOUNT_SECRET_KEY)
        s = s.lower()
        m.update(s)
        return m.hexdigest().lower()
        
    def do_password_reset(self, token, new_password):
        """
        Validates the password reset request and changes the password.

        :returns:   AccountPasswordReset
        """

        hash = self._calc_password_reset_hashed_token(token)
        
        try:
            req = _models.AccountPasswordReset.objects.select_related().get(hash=hash)
        except _models.AccountPasswordReset.DoesNotExist as e:
            raise AccountPasswordResetMissingError(cause=e)
        
        req.account.set_password(new_password)
        
        now = timezone.now()
        expiry = now + datetime.timedelta(seconds=app_settings.ACCOUNT_PASSWORD_RESET_EXPIRY_MINUTES*60)

        with transaction.commit_on_success():
            count = _models.AccountPasswordReset.objects\
                .filter(hash=hash, is_done=False, created__lt=expiry)\
                .update(is_done=True, changed=now)
            if count:
                req.account.save(update_fields=('password',))
            else:
                raise AccountPasswordResetExpiredError()
    
        req.is_done = True 
        req.changed = now
        return req
        
    def create_password_reset(self, account):
        """
        Creates a password reset request.

        This works by creating a unique token for the password reset request.
        Warning: Do not expose this token to users other than the intended 
        user. It is a security breach to let other users know about this token.

        There is at most one reset request for every account. 
        The reset creation process is throttled to prevent abuse. No more than
        one request can be created within ACCOUNT_PASSWORD_RESET_THRESHOLD_MINUTES.

        :type account:  AbstractAccount

        :returns:   str -- Alphanumeric token unique for the request. 
                    None -- if a request has already been created within the time threshold.
        """

        token = uuid.uuid4().hex 
        hash = self._calc_password_reset_hashed_token(token)
        
        try:
            req = _models.AccountPasswordReset.objects.get(account=account)
        except _models.AccountPasswordReset.DoesNotExist:
            # A race condition here (IntegrityError) is rare and benign. The worst is the user
            # gets an error message.
            req = _models.AccountPasswordReset.objects.create(hash=hash, account=account)
        else:
            now = timezone.now()
            delta = now - req.created
            delta_secs = delta.total_seconds()
            
            if 0 <= delta_secs and delta_secs <= app_settings.ACCOUNT_PASSWORD_RESET_THRESHOLD_MINUTES * 60:
                return None
                
            # Have to use this method as hash is primary key and Django
            # somehow does not support changing primary key.
            count = _models.AccountPasswordReset.objects\
                        .filter(account=account, hash=req.hash)\
                        .update(hash=hash, is_done=False, created=now)
            if not count:
                return None

        return token

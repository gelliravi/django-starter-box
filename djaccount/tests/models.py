from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.utils import timezone

from djbase.utils import mock

from djaccount.conf import settings as app_settings
from djaccount.models import Account
from djaccount.exceptions import *

class AccountManagerTest(TestCase):
    EMAIL       = Account.objects.normalize_email('john@doe.com')
    EMAIL_2     = Account.objects.normalize_email('mary@doe.com')
    FIRST_NAME  = 'John'
    PASSWORD    = '123'

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def _create(self):
        acc = Account.objects.create_user(email=self.EMAIL, first_name=self.FIRST_NAME, password=self.PASSWORD)
        return acc 

    def test_case_sensitive_email(self):
        acc = Account.objects.create_user(email=self.EMAIL.lower(), first_name=self.FIRST_NAME, password=self.PASSWORD)
        
        try:
            acc2 = Account.objects.get(email=self.EMAIL.upper())
        except Account.DoesNotExist:
            print 'WARNING: Email is case sensitive'
        finally:
            acc.delete()

    def test_create_user(self):
        acc = self._create()

        try:
            self.assertEqual(acc.first_name, self.FIRST_NAME)
            self.assertEqual(acc.email, Account.objects.normalize_email(self.EMAIL))
            self.assertEqual(acc.is_staff, False)
            self.assertEqual(acc.is_superuser, False)
            self.assertEqual(acc.is_active, False)
            self.assertTrue(acc.created <= timezone.now())
            self.assertEqual(acc.timezone, Account.INVALID_TIMEZONE)
        finally:
            acc.delete()

    def test_create_user_dup(self):
        acc = self._create()

        try:
            self.assertRaises(AccountEmailTakenError, self._create)
        finally:
            acc.delete()

    """
    Fails on SQLite
    def test_email_case_insensitive(self):
        acc = Account.objects.create_user(email=self.EMAIL.upper(), first_name=self.FIRST_NAME, password=self.PASSWORD)
        
        try:
            self.assertRaises(AccountEmailTakenError, self._create)
        finally:
            acc.delete()
    """

    def test_change_email(self):
        acc = self._create()

        try:
            code = Account.objects.calc_verify_code(account=acc)

            self.assertTrue(len(code) > 0)

            acc.is_active = True 
            Account.objects.change_email(account=acc, email=self.EMAIL_2)

            code2 = Account.objects.calc_verify_code(account=acc)
            
            self.assertFalse(acc.is_active)
            self.assertTrue(len(code2) > 0)
            self.assertNotEqual(code, code2)
            self.assertEqual(acc.email, Account.objects.normalize_email(self.EMAIL_2))

            acc = Account.objects.get(pk=acc.pk)
            self.assertFalse(acc.is_active)
            self.assertEqual(acc.email, Account.objects.normalize_email(self.EMAIL_2))            
        finally:
            acc.delete()

    def test_change_email_dup(self):
        acc = self._create()
        acc2 = Account.objects.create_user(email=self.EMAIL_2, first_name=self.FIRST_NAME, password=self.PASSWORD)
        
        try:
            acc.is_active = True
            acc.save()

            with self.assertRaises(AccountEmailTakenError):
                Account.objects.change_email(account=acc, email=self.EMAIL_2)

            self.assertTrue(acc.is_active)
            self.assertEqual(acc.email, self.EMAIL)

            acc = Account.objects.get(pk=acc.pk)
            self.assertTrue(acc.is_active)
            self.assertEqual(acc.email, self.EMAIL)
        finally:
            acc.delete()
            acc2.delete()

    def test_do_verify(self):
        acc = self._create()

        try:
            code = Account.objects.calc_verify_code(account=acc)

            res = Account.objects.do_verify(account=acc, code=code.upper())
            self.assertFalse(res)
            self.assertFalse(acc.is_active)

            acc = Account.objects.get(pk=acc.pk)
            self.assertFalse(acc.is_active)

            res = Account.objects.do_verify(account=acc, code=code)
            self.assertTrue(res)
            self.assertTrue(acc.is_active)

            acc = Account.objects.get(pk=acc.pk)
            self.assertTrue(acc.is_active)
        finally:
            acc.delete()

    def test_login(self):
        acc = self._create()

        req = self.factory.get('/')
        req.session = mock.Session()

        try:
            acc2 = Account.objects.login(email=acc.email, password=self.PASSWORD, request=req)
            self.assertTrue(acc2 is not None)
            self.assertEqual(acc2.pk, acc.pk)

            #req.user is not set
            #self.assertTrue(req.user)            
            #self.assertTrue(req.user.is_authenticated())
            #self.assertTrue(req.user.id, acc.id)
            #self.assertTrue(req.user.id, acc2.id)

            with self.assertRaises(AccountLoginError):
                Account.objects.login(email=acc.email, password=self.PASSWORD+'0', request=req)
        
            with self.assertRaises(AccountMissingError):
                Account.objects.login(email=acc.email+'0', password=self.PASSWORD, request=req)
        finally:
            acc.delete()

    def _test_password_reset(self, acc):
        token = Account.objects.create_password_reset(account=acc)
        self.assertTrue(len(token) > 0)
        
        token2 = Account.objects.create_password_reset(account=acc)
        self.assertEqual(token2, None)
        
        req = Account.objects.do_password_reset(token=token, new_password=self.PASSWORD*2)
        pwd_valid = req.account.check_password(self.PASSWORD*2)
        self.assertTrue(pwd_valid)
        self.assertTrue(acc.pk, req.account.pk)
        self.assertTrue(req.is_done)
        self.assertTrue(req.changed >= req.created)

        # check that it doesn't allow creating within threshold
        token2 = Account.objects.create_password_reset(account=acc)
        self.assertEqual(token2, None)
        
        # check whether new password is saved
        acc = Account.objects.get(pk=acc.pk)
        pwd_valid = acc.check_password(self.PASSWORD*2)
        self.assertTrue(pwd_valid)
        
        with self.assertRaises(AccountPasswordResetExpiredError): 
            Account.objects.do_password_reset(token=token, new_password=self.PASSWORD)
        
        acc = Account.objects.get(pk=acc.pk)
        pwd_valid = acc.check_password(self.PASSWORD*2)
        self.assertTrue(pwd_valid)

        with self.assertRaises(AccountPasswordResetMissingError): 
            Account.objects.do_password_reset(token=token+'0', new_password=self.PASSWORD)

        acc = Account.objects.get(pk=acc.pk)
        pwd_valid = req.account.check_password(self.PASSWORD*2)
        self.assertTrue(pwd_valid)

    def test_create_password_reset(self):
        acc = self._create()
        
        try:
            self._test_password_reset(acc)
        finally:
            acc.delete()

    def test_fb_load_or_create(self):
        cookies = {}
        app_id  = 'crap'
        app_secret = 'secret'

        req = self.factory.get('/')
        req.session = mock.Session()
        
        fb_user = mock.facebook.get_user_from_cookie(cookies, app_id, app_secret)
        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        try:
            self.assertEqual(ext.account.first_name, mock.facebook.PROFILE['first_name'])
            self.assertEqual(ext.account.last_name, mock.facebook.PROFILE['last_name'])
            self.assertEqual(ext.account.middle_name, mock.facebook.PROFILE['middle_name'])
            self.assertEqual(ext.account.locale, mock.facebook.PROFILE['locale'])
            self.assertEqual(ext.account.email, Account.objects.normalize_email(mock.facebook.PROFILE['email']))
            self.assertFalse(ext.account.is_active)
            self.assertFalse(ext.account.is_superuser)
            self.assertFalse(ext.account.is_staff)

            self.assertEqual(fb_user['uid'], ext.service_id)
            self.assertEqual(Account.objects.SERVICE_FB, ext.service)

            self.assertFalse(ext.account.has_usable_password())

            ext2 = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)
            self.assertEqual(ext2.pk, ext.pk)

            with self.assertRaises(AccountExternalSameEmailError):
                Account.objects.create_external_user(email=ext.account.email, first_name=ext.account.first_name, service=ext.service, service_id=ext.service_id)

            with self.assertRaises(AccountNoPasswordError):
                Account.objects.login(request=req, email=ext.account.email, password='1')
        finally:
            ext.delete()
            ext.account.delete()

    def test_fb_link(self):
        cookies = {}
        app_id  = 'crap'
        app_secret = 'secret'

        acc = self._create()
        acc2 = Account.objects.create_user(email=self.EMAIL_2, first_name=self.FIRST_NAME, password=self.PASSWORD)

        try:
            ext = Account.objects.fb_link(account=acc, cookies=cookies, app_id=app_id, app_secret=app_secret)
            self.assertEqual(ext.account.pk, acc.pk)

            with self.assertRaises(AccountExternalTakenError):
                Account.objects.link_external(account=acc2, service=ext.service, service_id=ext.service_id)

            exts = Account.objects.load_external(account=acc2)
            self.assertEqual(0, len(exts))

            exts = Account.objects.load_external(account=ext.account)
            self.assertEqual(1,len(exts))
            self.assertTrue(ext.service in exts)
            self.assertEqual(exts[ext.service], {'id':ext.service_id})            
        finally:
            acc.delete()
            acc2.delete()

    def test_login_external(self):
        cookies = {}
        app_id  = 'crap'
        app_secret = 'secret'

        req = self.factory.get('/')
        req.session = mock.Session()
        
        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        try:
            acc = Account.objects.login_external(request=req, service=ext.service, service_id=ext.service_id)
            self.assertTrue(acc.pk, ext.account.pk)

            with self.assertRaises(AccountMissingError):
                Account.objects.login_external(request=req, service=ext.service, service_id=ext.service_id+'0')                
        finally:
            ext.delete()
            ext.account.delete()

    def test_load_external(self):
        cookies = {}
        app_id  = 'crap'
        app_secret = 'secret'

        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        try:
            exts = Account.objects.load_external(account=ext.account)
            self.assertEqual(1,len(exts))
            self.assertTrue(ext.service in exts)
            self.assertEqual(exts[ext.service], {'id':ext.service_id})            
        finally:
            ext.delete()
            ext.account.delete()
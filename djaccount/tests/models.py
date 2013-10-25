from __future__ import unicode_literals

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import RequestFactory, Client
from django.test.utils import override_settings
from django.utils import timezone

from djbase.utils import mock

from djaccount.conf import settings as app_settings
from djaccount.models import AccountTest as Account, AccountExternalFriends
from djaccount.exceptions import *

def _unnormalize(email):
    if email:
        return email[0].lower() + email[1:].upper()
    return email 
    
@override_settings(
    AUTH_USER_MODEL='djaccount.AccountTest',
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',),
)
class AccountManagerTest(TransactionTestCase):
    EMAIL       = Account.objects.normalize_email('john@doe.com')
    EMAIL_2     = Account.objects.normalize_email('mary@doe.com')
    FIRST_NAME  = 'John'
    PASSWORD    = '123'

    def setUp(self):
        self.acc        = Account.objects.create_user(email=self.EMAIL, first_name=self.FIRST_NAME, password=self.PASSWORD)
        self.factory    = RequestFactory()

    def test_case_sensitive_email(self):
        try:
            acc2 = Account.objects.get(email=_unnormalize(self.acc.email))
        except Account.DoesNotExist:
            print 'WARNING: Database email column is case sensitive'

    def test_create_user(self):
        acc = self.acc
        self.assertEqual(acc.first_name, self.FIRST_NAME)
        self.assertEqual(acc.email, Account.objects.normalize_email(self.EMAIL))
        self.assertEqual(acc.is_staff, False)
        self.assertEqual(acc.is_superuser, False)
        self.assertEqual(acc.is_active, False)
        self.assertTrue(acc.created <= timezone.now())
        self.assertEqual(acc.timezone, Account.INVALID_TIMEZONE)

    @override_settings(ACCOUNT_LOWER_EMAIL=True)
    def test_lower_email_true(self):
        email1  = Account.objects.normalize_email('john@doe.com')
        email2  = Account.objects.normalize_email('jOhN@DoE.com')        
        self.assertEqual(email1, email2)

    @override_settings(ACCOUNT_LOWER_EMAIL=False)
    def test_lower_email_false(self):
        email1  = Account.objects.normalize_email('john@doe.com')
        email2  = Account.objects.normalize_email('jOhN@DoE.com')        
        self.assertNotEqual(email1, email2)

    def test_create_user_dup(self):
        with self.assertRaises(AccountEmailTakenError):
            Account.objects.create_user(email=self.acc.email, first_name=self.FIRST_NAME, password=self.PASSWORD)
        
    def test_change_email(self):
        acc = self.acc
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
    
    def test_change_email_dup(self):
        acc = self.acc

        acc.is_active = True
        acc.save()

        acc2 = Account.objects.create_user(email=self.EMAIL_2, first_name=self.FIRST_NAME, password=self.PASSWORD)

        with self.assertRaises(AccountEmailTakenError):
            Account.objects.change_email(account=acc, email=self.EMAIL_2)

        self.assertTrue(acc.is_active)
        self.assertEqual(acc.email, self.EMAIL)

        acc = Account.objects.get(pk=acc.pk)
        self.assertTrue(acc.is_active)
        self.assertEqual(acc.email, self.EMAIL)
        
    def test_do_verify(self):
        acc = self.acc

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
    
    def test_login(self):
        acc = self.acc 

        req = self.factory.get('/')
        req.session = mock.Session()

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

    def test_create_password_reset(self):
        acc = self.acc        
    
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

    def test_fb_load_or_create(self):
        cookies     = {}
        app_id      = 'crap'
        app_secret  = 'secret'

        req = self.factory.get('/')
        req.session = mock.Session()
        
        self.acc.delete()

        fb_user = mock.facebook.get_user_from_cookie(cookies, app_id, app_secret)
        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        self.assertEqual(ext.account.first_name, mock.facebook.PROFILE['first_name'])
        self.assertEqual(ext.account.last_name, mock.facebook.PROFILE['last_name'])
        self.assertEqual(ext.account.middle_name, mock.facebook.PROFILE['middle_name'])
        self.assertEqual(ext.account.locale, mock.facebook.PROFILE['locale'])
        self.assertEqual(ext.account.email, Account.objects.normalize_email(mock.facebook.PROFILE['email']))
        self.assertFalse(ext.account.is_active)
        self.assertFalse(ext.account.is_superuser)
        self.assertFalse(ext.account.is_staff)
        self.assertEqual(AccountExternalFriends.objects.filter(account=ext.account).count(), len(mock.facebook.PROFILE['friends']['data']))

        self.assertEqual(fb_user['uid'], ext.service_id)
        self.assertEqual(Account.objects.SERVICE_FB, ext.service)

        self.assertFalse(ext.account.has_usable_password())

        ext2 = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)
        self.assertEqual(ext2.pk, ext.pk)

        with self.assertRaises(AccountExternalSameEmailError):
            Account.objects.create_external_user(email=ext.account.email, first_name=ext.account.first_name, service=ext.service, service_id=ext.service_id)

        with self.assertRaises(AccountNoPasswordError):
            Account.objects.login(request=req, email=ext.account.email, password='1')

    def test_fb_link(self):
        cookies     = {}
        app_id      = 'crap'
        app_secret  = 'secret'

        acc     = self.acc
        acc2    = Account.objects.create_user(email=self.EMAIL_2, first_name=self.FIRST_NAME, password=self.PASSWORD)

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

    def test_login_external(self):
        cookies     = {}
        app_id      = 'crap'
        app_secret  = 'secret'

        self.acc.delete()

        req = self.factory.get('/')
        req.session = mock.Session()
        
        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        acc = Account.objects.login_external(request=req, service=ext.service, service_id=ext.service_id)
        self.assertTrue(acc.pk, ext.account.pk)

        with self.assertRaises(AccountMissingError):
            Account.objects.login_external(request=req, service=ext.service, service_id=ext.service_id+'0')                

    def test_load_external(self):
        cookies     = {}
        app_id      = 'crap'
        app_secret  = 'secret'

        self.acc.delete()

        ext = Account.objects.fb_load_or_create(cookies=cookies, app_id=app_id, app_secret=app_secret)

        exts = Account.objects.load_external(account=ext.account)
        self.assertEqual(1,len(exts))
        self.assertTrue(ext.service in exts)
        self.assertEqual(exts[ext.service], {'id':ext.service_id})            

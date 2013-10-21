from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

from djaccount.models import Account
from djaccount.exceptions import *

class AccountManagerTest(TestCase):
    EMAIL       = Account.objects.normalize_email('john@doe.com')
    EMAIL_2     = Account.objects.normalize_email('mary@doe.com')
    FIRST_NAME  = 'John'
    PASSWORD    = '123'

    def _create(self):
        acc = Account.objects.create_user(email=self.EMAIL, first_name=self.FIRST_NAME, password=self.PASSWORD)
        return acc 

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


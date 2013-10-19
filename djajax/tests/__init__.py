from django.conf import settings
from django.utils import timezone
from django.test import TestCase
from djbase.utils import parse_iso_datetime
from djbase.utils.json import encode as json_encode

import json

class DjAjaxIntegrationTest(TestCase):
    PREFIX          = '/djajax/djajax.tests.'
    PREFIX_CUSTOM   = '/djajax/'

    urls = 'djajax.tests.urls'
    
    def setUp(self):
        settings.INSTALLED_APPS += ('djajax.tests',)

    def test_missing(self):
        response = self.client.post(self.__class__.PREFIX + 'missing')
        result = json.loads(response.content)
        self.assertEqual(result['error']['type'], 'InvalidMethodError')
        self.assertEqual(result['data'], None)

    def test_wrong_method(self):
        response = self.client.get(self.__class__.PREFIX + 'post_no_param')
        result = json.loads(response.content)
        self.assertEqual(result['error']['type'], 'InvalidMethodError')
        self.assertEqual(result['data'], None)

    def test_post_no_param(self):
        response = self.client.post(self.__class__.PREFIX + 'post_no_param')
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], 'success')

    def test_post_with_params(self):
        param1 = 1234
        param2 = 'hello world!'
        data = {'param1': param1, 'param2' : param2}

        response = self.client.post(self.__class__.PREFIX + 'post_with_params', {'data': json_encode(data)})
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], data)

    def test_post_with_params_data_error(self):
        response = self.client.post(self.__class__.PREFIX + 'post_with_params', {'data': 'invalid'})
        result = json.loads(response.content)
        self.assertEqual(result['error']['type'], 'InvalidDataError')
        self.assertEqual(result['data'], None)

    def test_post_with_form_params(self):
        param1 = '2013-01-03T01:02:03Z'
        param2 = 'hello'
        data = {'param1': param1, 'param2' : param2}

        response = self.client.post(self.__class__.PREFIX + 'post_with_form_params', {'data': json_encode(data)})
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], data)

    def test_post_with_form_params_error(self):
        param1 = None
        param2 = 'hello world'
        data = {'param1': param1, 'param2' : param2}

        response = self.client.post(self.__class__.PREFIX + 'post_with_form_params', {'data': json_encode(data)})
        result = json.loads(response.content)
        self.assertEqual(result['error']['type'], 'InvalidParamError')
        self.assertTrue('param2' in result['error']['data'])
        self.assertTrue('param1' not in result['error']['data'])
        self.assertTrue(result['error']['data']['param2'][0] != '')
        self.assertEqual(result['data'], None)

    def test_get_with_form_params(self):
        param1 = '2013-01-03T01:02:03Z'
        param2 = 'hello'
        data = {'param1': param1, 'param2' : param2}

        response = self.client.get(self.__class__.PREFIX + 'get_with_form_params', {'data': json_encode(data)})
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], data)

    def test_multi_get(self):
        response = self.client.get(self.__class__.PREFIX_CUSTOM + 'multi.get')
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], 'success')

    def test_multi_post(self):
        response = self.client.post(self.__class__.PREFIX_CUSTOM + 'multi.post')
        result = json.loads(response.content)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['data'], 'success')

from __future__ import unicode_literals

import uuid
import urllib2
import re
import gzip
from unittest import skipIf

from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.core.files.base import ContentFile
from django.test import TransactionTestCase
from django.test.client import RequestFactory, Client
from django.test.utils import override_settings
from django.utils import timezone

from djcdn.templatetags import cdn
from djcdn import filters

_STATIC_PATH  = 'test-static-'+uuid.uuid4().hex+"/"
_DEFAULT_PATH = 'test-media-'+uuid.uuid4().hex+"/"

_STATIC_URL  = '//s3.amazonaws.com/%s/%s' % (settings.AWS_STORAGE_BUCKET_NAME, _STATIC_PATH)
_DEFAULT_URL = '//s3.amazonaws.com/%s/%s' % (settings.AWS_STORAGE_BUCKET_NAME, _DEFAULT_PATH)

_aws_bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
_aws_access = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
_aws_secret = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)

if _aws_secret and _aws_bucket and _aws_access:
    _skip = False
else:
    _skip = True 

@override_settings(
    DEFAULT_FILE_STORAGE  = 'djcdn.storage.s3.DefaultStorage',
    STATICFILES_STORAGE   = 'djcdn.storage.s3.VersionedStaticStorage',
    CDN_STATIC_S3_PATH    = _STATIC_PATH,
    CDN_DEFAULT_S3_PATH   = _DEFAULT_PATH,
    MEDIA_ROOT            = '/%s/' % _DEFAULT_PATH,
    MEDIA_URL             = _DEFAULT_URL,
    STATIC_ROOT           = "/%s/" % _STATIC_PATH,
    STATIC_URL            = _STATIC_URL,
    CDN_STATIC_FILTERS    = {
        'css'   : ('filters.cssmin', 'filters.csspath'),
        'js'    : ('filters.slimit',),
        'png'   : ('filters.pngcrush',),
        'jpg'   : ('filters.jpegoptim',),
        'jpeg'  : ('filters.jpegoptim',),
    },
    CDN_STATIC_COMPRESSED_TYPES = ('css', 'js'), # Lowercase
    CDN_STATIC_EXPIRY_AGE =  3600 * 24 * 365, # seconds
    CDN_DEFAULT_FILTERS    = {
        'css'   : ('filters.cssmin', 'filters.csspath'),
        'js'    : ('filters.slimit',),
        'png'   : ('filters.pngcrush',),
        'jpg'   : ('filters.jpegoptim',),
        'jpeg'  : ('filters.jpegoptim',),
    },
    CDN_DEFAULT_COMPRESSED_TYPES = ('css', 'js'), # Lowercase
    CDN_DEFAULT_EXPIRY_AGE =  3600 * 24 * 365, # seconds
)
@skipIf(_skip, 'Please input AWS settings')
class StorageTest(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _check_upload(self, body_min, is_gzip):
        request = self.factory.get('/')
        request.META['HTTP_ACCEPT_ENCODING'] = 'gzip,deflate' if is_gzip else ''
        context = {'request': request}

        url = cdn.cdn(path='folder/a.css', context=context, type='DEFAULT')
        self.assertTrue(url.startswith(settings.MEDIA_URL))

        request = urllib2.Request('http:'+url )
        response = urllib2.urlopen(request)
        
        expires = response.info().getheader('Expires')
        cache   = response.info().getheader('Cache-Control')
        encoding = response.info().getheader('Content-Encoding')

        self.assertTrue('max-age' in cache) 
        self.assertEqual(response.info().getheader('Content-Type'), 'text/css')
        self.assertTrue(re.match(r'\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2} GMT', expires))

        if is_gzip:
            self.assertEqual('gzip', encoding)
            buf = ContentFile( response.read())
            f = gzip.GzipFile(fileobj=buf)
            ret_body = f.read()
            self.assertEqual(ret_body, body_min)
        else:
            self.assertTrue(not encoding or 'gzip' not in encoding)
            ret_body = response.read()
            self.assertEqual(ret_body, body_min)

    def test_default(self):
        # Test with some unicode characters
        css_body = 'body   {        background: url("\u1234");  } '
        css_output_file = filters.cssmin(ContentFile(css_body))
        css_body_min = css_output_file.read()

        self.assertFalse(b'   ' in css_body_min)

        storage = DefaultStorage()
        storage.save('folder/a.css', ContentFile(css_body))

        self._check_upload(is_gzip=False, body_min=css_body_min)
        self._check_upload(is_gzip=True, body_min=css_body_min)

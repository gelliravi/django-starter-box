from __future__ import unicode_literals

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase 
from django.test.utils import override_settings

from djcdn import filters

@override_settings(
    STATIC_ROOT = '/static/',
    STATIC_URL = '//1234.cloudfront.net/static/',
)
class CssPathTest(TestCase):
    def test(self):
        test_data = (
            ('@import url("%scss/main.css")' % settings.STATIC_ROOT, 
             '@import url("%scss/main.css")' % settings.STATIC_URL),

            ('@import url(\'%scss/main.css\')' % settings.STATIC_ROOT, 
             '@import url(\'%scss/main.css\')' % settings.STATIC_URL),   

            ('@import url(%scss/main.css)' % settings.STATIC_ROOT, 
             '@import url(%scss/main.css)' % settings.STATIC_URL),

            # mismatch quotes
            ('@import url(\'%scss/main.css")' % settings.STATIC_ROOT, 
             '@import url(\'%scss/main.css")' % settings.STATIC_ROOT),

            ('@import url( "%scss/main.css" )' % settings.STATIC_ROOT, 
             '@import url( "%scss/main.css" )' % settings.STATIC_URL),

            ('@import "%scss/main.css"' % settings.STATIC_ROOT, 
             '@import "%scss/main.css"' % settings.STATIC_URL),

            ('@import \'%scss/main.css\')' % settings.STATIC_ROOT, 
             '@import \'%scss/main.css\')' % settings.STATIC_URL),   

            # no quotes
            ('@import %scss/main.css' % settings.STATIC_ROOT, 
             '@import %scss/main.css' % settings.STATIC_ROOT),

            # mismatch quotes
            ('@import \'%scss/main.css"' % settings.STATIC_ROOT, 
             '@import \'%scss/main.css"' % settings.STATIC_ROOT),

            ('@import  "%scss/main.css" screen, projected' % settings.STATIC_ROOT, 
             '@import  "%scss/main.css" screen, projected' % settings.STATIC_URL),

            ('iurl("%scss/main.css") screen, projected' % settings.STATIC_ROOT, 
             'iurl("%scss/main.css") screen, projected' % settings.STATIC_ROOT),   

            ('iurl("css/main.css") screen, projected', 
             'iurl("css/main.css") screen, projected'),      
        )

        prefices = ('', 'body{} ')
        suffices = ('', ';', ' screen')
        input_all = ''
        expected_all = ''

        for prefix in prefices:
            for suffix in suffices:
                for pairs in test_data:
                    input = prefix + pairs[0] + suffix 
                    expected = prefix + pairs[1] + suffix 
                    output = filters.csspath(ContentFile(input)).read()
                    self.assertEqual(output, expected)

                    input_all += input + "\n"
                    expected_all += expected + "\n"

        output_all = filters.csspath(ContentFile(input_all)).read()
        self.assertEqual(output_all, expected_all)

    def test_version(self):
        version = '20131023-12345678'
        test_data = (
            ('@import  "%scss/main.css" screen, projected' % settings.STATIC_ROOT, 
             '@import  "%s%s/css/main.css" screen, projected' % (settings.STATIC_URL, version)),
        )

        for pairs in test_data:
            input = pairs[0] 
            expected = pairs[1]
            output = filters.csspath(ContentFile(input), version_str=version).read()
            self.assertEqual(output, expected)



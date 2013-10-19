from django.utils import timezone
from django.utils.translation import ugettext as _
from django.test import TestCase
from djbase.utils import json_stringify

from datetime import datetime, date

class JSONTest(TestCase):
    class SimpleObject(object):
        def to_json(self):
            return 'hello'

    def test_encode(self):
        data = (
            (_('hello world'), '"%s"' % _('hello world')),
            (None, "null"),
            (JSONTest.SimpleObject(), '"hello"'),
            (timezone.make_aware(datetime(2013, 1, 30, 11, 12, 13, 0), timezone=timezone.utc), '"2013-01-30T11:12:13Z"'),
            (date(2013, 1, 30), '"2013-01-30"'),
        )

        for test in data:
            test_value      = test[0]
            test_expected   = test[1] 

            encoded = json_stringify(test_value)
            self.assertEqual(encoded, test_expected)

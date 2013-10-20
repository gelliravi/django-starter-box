from __future__ import unicode_literals

from django.utils import timezone
from django.utils.translation import ugettext as _
from django.test import TestCase
from djbase.utils import parse_iso_datetime
from djbase.utils.json import encode as json_encode

from datetime import datetime, date

class JSONTest(TestCase):
    class SimpleObject(object):
        def to_json(self):
            return 'hello'

    def test_encode(self):
        data = (
            (_('Test Only. Do Not Translate'), '"%s"' % _('Test Only. Do Not Translate')),
            (None, "null"),
            (JSONTest.SimpleObject(), '"hello"'),
            (timezone.make_aware(datetime(2013, 1, 30, 11, 12, 13, 0), timezone=timezone.utc), '"2013-01-30T11:12:13Z"'),
            (date(2013, 1, 30), '"2013-01-30"'),
        )

        for test in data:
            test_input      = test[0]
            test_expected   = test[1] 

            output = json_encode(test_input)
            self.assertEqual(output, test_expected)

class UtilsTest(TestCase):
    def test_parse_iso_datetime(self):
        data = (
            ('2013-01-30T11:12:13Z', timezone.make_aware(datetime(2013, 1, 30, 11, 12, 13, 0), timezone=timezone.utc)),
            ('2013-01-30T11:12:13+08:00', timezone.make_aware(datetime(2013, 1, 30, 03, 12, 13, 0), timezone=timezone.utc)),
        )

        for test in data:
            test_input      = test[0]
            test_expected   = test[1] 

            output = parse_iso_datetime(test_input)
            self.assertEqual(output, test_expected)

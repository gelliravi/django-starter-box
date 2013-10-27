from __future__ import unicode_literals

from django.test import TestCase
from django.db import models
from djbase.models import PickleField, FixedCharField

from . import PickleFieldTestModel, FixedCharFieldTestModel

class CustomType(list):
    test = []

class PickleFieldTest(TestCase):
    def test(self):
        test_data = (
            123, (), (None,), (1,2), [], [1,2], {}, {1:2, 3:4}, {'1': 1},
            CustomType(), 
        )

        test_data2 = [e for e in test_data]
        test_data2.append(test_data)

        for input in test_data2:
            m = PickleFieldTestModel(required=input)
            self.assertEqual(m.optional, (1,2))
            self.assertEqual(m.required, input)

            m.clean()
            m.save()
            self.assertEqual(m.optional, (1,2))
            self.assertEqual(m.required, input)

            m2 = PickleFieldTestModel.objects.get(pk=m.pk)
            self.assertEqual(m2.required, m.required)
            self.assertEqual(m2.optional, m.optional)

        test_data2.append(None)

        for input in test_data2:
            m3 = PickleFieldTestModel(required={}, optional=input)
            self.assertEqual(m3.optional, input)
            self.assertEqual(m3.required, {})

            m3.clean()
            m3.save()
            self.assertEqual(m3.optional, input)
            self.assertEqual(m3.required, {})

            m4 = PickleFieldTestModel.objects.get(pk=m3.pk)
            self.assertEqual(m4.optional, input)
            self.assertEqual(m4.required, {})

class FixedCharFieldTest(TestCase):
    def test(self):
        test_data = (
            ('', ''),
            ('   ', ''),
            (' a ','a'),
            (b'  ', ''),
            # (None, None), # Cannot use None as it is treated as Null
        )

        for pairs in test_data:
            input = pairs[0]
            expected = pairs[1]

            m = FixedCharFieldTestModel(required=input)
            self.assertEqual(m.required, expected)
            self.assertEqual(m.optional, 'a')

            m.clean()
            m.save()
            self.assertEqual(m.required, expected)
            self.assertEqual(m.optional, 'a')

            m2 = FixedCharFieldTestModel.objects.get(pk=m.pk)
            self.assertEqual(m2.required, m.required)
            self.assertEqual(m2.optional, m.optional)

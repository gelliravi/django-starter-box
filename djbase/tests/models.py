from __future__ import unicode_literals

from django.test import TestCase
from django.db import models
from djbase.models import PickleField

from . import PickleModelTest

class CustomType(list):
    test = []

class PickleFieldTest(TestCase):
    def test(self):
        test_data = (
            None, 123, (1,2), [], {}, {1:2, 3:4}, {'1': 1},
            CustomType()
        )

        test_data2 = [e for e in test_data]
        test_data2.append(test_data)

        for input in test_data2:
            m = PickleModelTest(p=input)
            self.assertEqual(m.p2, (1,2))
            m.save()

            m2 = PickleModelTest.objects.get(pk=m.pk)
            self.assertEqual(m.p, m2.p)
            self.assertEqual(m2.p2, (1,2))


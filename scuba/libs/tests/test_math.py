"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.libs.math import Math


class TestMath(TestCase):
    def test_isfloat(self):
        """
        Test if a value is a float
        """
        self.assertFalse(Math.isfloat('s12'))
        self.assertTrue(Math.isfloat('1.1234'))
        self.assertTrue(Math.isfloat('-1.1234'))
        self.assertTrue(Math.isfloat('1'))
        self.assertTrue(Math.isfloat('-1'))
        self.assertTrue(Math.isfloat('1.0'))
        self.assertTrue(Math.isfloat('.2'))
        self.assertTrue(Math.isfloat('.1'))

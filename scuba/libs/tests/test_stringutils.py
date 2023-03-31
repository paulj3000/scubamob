"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.libs.stringutils import StringUtils


class TestStringUtils(TestCase):
    def test_generate_url_from_string(self):
        """
        Test simple user get name
        """
        # just for readability and pep8 stuff
        gen_url = StringUtils.generate_url_from_string
        self.assertEqual(gen_url('Whites Point'), 'whites-point')
        self.assertEqual(gen_url('Whites    Point'), 'whites-point')
        self.assertEqual(gen_url('Whites Point 987'), 'whites-point-987')

    def test_generate_random_string(self):
        gen_str = StringUtils.generate_random_string

        for some_len in [10, 5, 3, 20]:
            some_str = gen_str(some_len)
            self.assertEqual(len(some_str), some_len)
            self.assertTrue(some_str.isupper())

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from unittest.mock import patch

from django.test import TestCase

from scuba.accounts.models import User
from scuba.libs.stringutils import StringUtils


class TestStringUtils(TestCase):
    def test_generate_url_from_string(self):
        """
        Testing the conversion of a simple string to a
        url-safe string
        """
        # just for readability and pep8 stuff
        gen_url = StringUtils.generate_url_from_string
        self.assertEqual(gen_url('Whites Point'), 'whites-point')
        self.assertEqual(gen_url('Whites    Point'), 'whites-point')
        self.assertEqual(gen_url('Whites Point 987'), 'whites-point-987')

    def test_generate_random_string(self):
        """
        Testing the generation of a random string, case sensitive
        """
        gen_str = StringUtils.generate_random_string

        for some_len in [10, 5, 3, 20]:
            some_str = gen_str(some_len)
            self.assertEqual(len(some_str), some_len)
            self.assertTrue(some_str.isupper())

    def test_generate_random_string_case_insensitive(self):
        """
        Testing the generation of a random string, case insensitive
        """
        gen_str = StringUtils.generate_random_string_case_insensitive

        for some_len in [10, 5, 3, 20]:
            some_str = gen_str(some_len)
            self.assertEqual(len(some_str), some_len)

    def test_get_random_password_string_uses_secrets(self):
        """
        get_random_password_string must draw from the secrets module (not
        the non-cryptographic random module) for password generation.
        """
        with patch('scuba.libs.stringutils.secrets.choice', return_value='x') as mock_choice:
            password = StringUtils.get_random_password_string(12)

        self.assertEqual(len(password), 12)
        self.assertEqual(mock_choice.call_count, 12)

    def test_get_random_password_string_length_and_charset(self):
        import string as string_module

        password = StringUtils.get_random_password_string(16)
        self.assertEqual(len(password), 16)

        allowed = set(string_module.ascii_letters + string_module.digits + string_module.punctuation)
        self.assertTrue(set(password) <= allowed)

    def test_generate_short_id_queries_the_passed_model(self):
        """
        generate_short_id is a plain staticmethod -- it must query
        uniqueness against the model explicitly passed as `model_cls`,
        not implicitly bind to StringUtils itself.
        """
        short_id = StringUtils.generate_short_id(User, 6, 'act', key='aws_id')
        self.assertTrue(short_id.startswith('act'))
        self.assertEqual(len(short_id), 9)
        self.assertFalse(User.objects.filter(aws_id=short_id).exists())

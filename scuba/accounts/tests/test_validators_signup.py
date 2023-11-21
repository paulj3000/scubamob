"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.accounts.validators.signup import validate_password, validate_username


class TestValidatorSignup(TestCase):
    def test_validator_password(self):
        """
        Test password validator
        """
        self.assertTrue(validate_password("test1234"))
        self.assertTrue(validate_password("test1234567"))
        self.assertFalse(validate_password("tes"))
        self.assertFalse(validate_password("t"))
        self.assertFalse(validate_password("te"))
        self.assertFalse(validate_password("123456789012345678901234te"))

    def test_validator_username(self):
        """
        Test password username
        """
        self.assertTrue(validate_username("test1234"))
        self.assertTrue(validate_username("test1234567"))
        self.assertTrue(validate_username("test5"))
        self.assertFalse(validate_username("test"))
        self.assertFalse(validate_username("tes"))
        self.assertFalse(validate_username("t"))
        self.assertFalse(validate_username("te"))
        self.assertFalse(validate_username("123456789012345678901234te"))

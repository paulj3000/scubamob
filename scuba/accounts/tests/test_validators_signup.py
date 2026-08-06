"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from scuba.accounts.validators.signup import validate_password, validate_username


class TestValidatorSignup(TestCase):
    def test_validator_password(self):
        """
        Test password validator
        """
        validate_password("test1234567")  # does not raise
        validate_password("Str0ngPassw0rd!")  # does not raise

        with self.assertRaises(ValidationError):
            validate_password("test1234")  # too common

        with self.assertRaises(ValidationError):
            validate_password("tes")

        with self.assertRaises(ValidationError):
            validate_password("t")

        with self.assertRaises(ValidationError):
            validate_password("te")

        with self.assertRaises(ValidationError):
            validate_password("123456789012345678901234te")

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

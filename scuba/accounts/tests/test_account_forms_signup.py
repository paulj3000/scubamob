"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.accounts.models import User
from scuba.accounts.forms.signup import SignupForm


class TestAccountFormSignup(TestCase):
    fixtures = ["test_users.json"]

    def test_good_form(self):
        """
        Test simple user get name
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1970-04-01',
            'email': 'test@newuser.com',
            'password': 'testpassword',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        form = SignupForm(data=data)
        self.assertTrue(form.is_valid())

        new_user = form.save()
        self.assertIsNotNone(new_user.pk_as_str)

    def test_bad_form_russia(self):
        """
        Test if the user came from russia
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1970-04-01',
            'email': 'test@newuser.ru',
            'password': 'testpassword',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"], ["This request cannot be processed"]
        )

    def test_duplicate_email(self):
        """
        Test if the email address is a duplicate
        """
        email = 'test2@tester.com'
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1970-04-01',
            'email': email,
            'password': 'testpassword',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"], [f"{email} is already registered"],
        )

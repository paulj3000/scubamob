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
            'username': 'newtestuser',
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
            'username': 'russia',
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
            'username': 'duplicateuser',
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

    def test_duplicate_username(self):
        """
        Test if the email address is a duplicate
        """
        username = 'testtester'
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': username,
            'date_of_birth': '1970-04-01',
            'email': 'xxx@duplicateusername.com',
            'password': 'testpassword',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], [f"{username} is already registered"],
        )

    def test_bad_password_length(self):
        """
        Test a bad password, it has to be at least 4 characters
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'newtestuser',
            'date_of_birth': '1970-04-01',
            'email': 'test@newuser.com',
            'password': 'x',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        for x in range(1, 4):
            passwd = 'x' * x
            data['password'] = passwd

            form = SignupForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors["password"], ['Your password must be between 4 and 20 characters'],
            )

        data['password'] = 'x' * 21
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ['Your password must be between 4 and 20 characters'],
        )

    def test_bad_username_length(self):
        """
        Test a bad password, it has to be at least 4 characters
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1970-04-01',
            'email': 'test@newuser.com',
            'password': 'xxxxxxxx',
            'ip_address': '0.0.0.0',
            'is_spam': False,
        }

        for x in range(1, 5):
            username = 'x' * x
            data['username'] = username

            form = SignupForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors['username'], [f'{username} is a bad length']
            )

        data['username'] = 'x' * 41
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['username'], ['Ensure this value has at most 40 characters (it has 41).']
        )

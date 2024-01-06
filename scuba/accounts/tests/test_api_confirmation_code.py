"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User, UserConfirmationCode
from scuba.accounts.exceptions import InvalidConfirmationCodeException


class TestConfirmationCode(TestCase):
    fixtures = ["test_users.json"]

    def test_generate_confirmation_code(self):
        """
        Test generate confirmation codes
        """
        user = User.objects.get(email='foo@nowhere.com')
        code1 = user.generate_confirmation_code()

        self.assertEqual(len(str(code1.code)), 6)

    def test_invalid_code_tested(self):
        user = User.objects.get(email='foo@nowhere.com')
        code = user.generate_confirmation_code()
        to_test = code.code + 10

        with self.assertRaises(InvalidConfirmationCodeException) as _:
            user.verify_confirmation_code(to_test)

    def test_generate_multiple_confirmation_code(self):
        """
        Test generate multiple confirmation codes
        """
        user = User.objects.get(email='foo@nowhere.com')
        code1 = user.generate_confirmation_code()
        self.assertEqual(len(str(code1.code)), 6)

        code2 = user.generate_confirmation_code()
        self.assertEqual(len(str(code2.code)), 6)

        code3 = user.generate_confirmation_code()
        self.assertEqual(len(str(code3.code)), 6)

    def test_reedeem_confirmation_code(self):
        """
        Test the redeeming of cnfirmation codes
        """
        user = User.objects.get(email='foo@nowhere.com')
        code2 = user.generate_confirmation_code()

        try:
            user.verify_confirmation_code(code2.code)
            code = user.confirmation_codes.get(code=code2.code)
            self.assertTrue(code.redeemed)
        except InvalidConfirmationCodeException:
            self.fail("Code was not found")
        except UserConfirmationCode.DoesNotExist:
            self.fail("Code was not found")

    def test_get_and_set_confirmation_code(self):
        """
        Test setting good password
        """
        os.environ['NO_MAIL'] = 'True'
        user = User.objects.get(email='foo@nowhere.com')

        # verify the user is NOT confirmed
        self.assertFalse(user.confirmed)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/signup/confirmation_code', format='json')
        self.assertEqual(response.status_code, 200)

        code = user.confirmation_codes.all().first()
        payload = {
            'code': code.code
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEqual(response.status_code, 200)

        # verify the user is confirmed
        user = User.objects.get(email='foo@nowhere.com')
        self.assertTrue(user.confirmed)

    def test_get_and_set_invalid_confirmation_code(self):
        """
        Test setting good password
        """
        os.environ['NO_MAIL'] = 'True'
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/signup/confirmation_code', format='json')
        self.assertEqual(response.status_code, 200)

        code = user.confirmation_codes.all().first()
        payload = {
            'code': code.code - 10
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEqual(response.status_code, 400)

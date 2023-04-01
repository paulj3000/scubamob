"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.accounts.exceptions import InvalidConfirmationCodeException
from scuba.content.exceptions import InvalidConfigrationException


class TestConfirmationCode(TestCase):
    @staticmethod
    def create_test_user():
        return User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-04-01',
            email='foo@nowhere.com')

    def test_generate_confirmation_code(self):
        """
        Test generate confirmation codes
        """
        user = self.create_test_user()
        code1 = user.generate_confirmation_code()

        self.assertEqual(len(str(code1.code)), 6)

    def test_invalid_code_tested(self):
        user = self.create_test_user()
        code = user.generate_confirmation_code()
        to_test = code.code + 10

        with self.assertRaises(InvalidConfirmationCodeException) as context:
            user.verify_confirmation_code(to_test)

    def test_generate_multiple_confirmation_code(self):
        """
        Test generate multiple confirmation codes
        """
        user = self.create_test_user()
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
        user = self.create_test_user()
        code1 = user.generate_confirmation_code()
        code2 = user.generate_confirmation_code()
        code3 = user.generate_confirmation_code()

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
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        try:
            response = client.get('/api/signup/confirmation_code', format='json')
        except InvalidConfigrationException:
            pass

        code = user.confirmation_codes.all().first()
        payload = {
            'code': code.code
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_and_set_invalid_confirmation_code(self):
        """
        Test setting good password
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        try:
            response = client.get('/api/signup/confirmation_code', format='json')
        except InvalidConfigrationException:
            pass

        code = user.confirmation_codes.all().first()
        payload = {
            'code': code.code - 10
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEqual(response.status_code, 400)

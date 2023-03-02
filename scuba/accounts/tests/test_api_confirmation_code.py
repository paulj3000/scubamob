"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class APIConfirmationCode(TestCase):
    @staticmethod
    def create_test_user():
        return User.objects.create(
            first_name='First',
            last_name='Last',
            username='someuser',
            email='foo@nowhere.com')

    @staticmethod
    def generate_test_confirmation_code():
        return random.randint(10000, 99999)
        return f'newuser_{rnd}'

    def test_get_confirmation_code(self):
        """
        Test getting confirmation code
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/signup/confirmation_code', format='json')
        self.assertIn('code', response.json())
        self.assertTrue(100000 <= response.json().get('code') <= 999999)

    def test_validate_confirmation_code_success(self):
        """
        Test submitting good confirmation code
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/signup/confirmation_code', format='json')
        result_code = response.json().get('code')
        payload = {
            'code': response.json().get('code')
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEquals(response.status_code, 200)
        self.assertIn('code', response.json())
        self.assertTrue(response.json()['code'])

    def test_validate_confirmation_code_failure(self):
        """
        Test submitting bad confirmation code
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        # get a temporary status code
        response = client.get('/api/signup/confirmation_code', format='json')
        result_code = response.json().get('code')

        test_code = self.generate_test_confirmation_code()
        while test_code == result_code:
            test_code = self.generate_test_confirmation_code()

        payload = {
            'code': test_code
        }

        response = client.post('/api/signup/confirmation_code/', payload, format='json')
        self.assertEquals(response.status_code, 400)
        self.assertIn('code', response.json())
        self.assertFalse(response.json()['code'])

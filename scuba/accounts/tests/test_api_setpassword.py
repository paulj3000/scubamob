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


class APISetPassword(TestCase):
    @staticmethod
    def create_test_user():
        return User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-04-01',
            email='foo@nowhere.com')

    def test_set_good_password(self):
        """
        Test setting good password
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'password': "ThisisAGoodPassword%",
        }

        response = client.put('/api/signup/password/', payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_set_bad_password(self):
        """
        Test setting bad password
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'password': "xxx",
        }

        response = client.put('/api/signup/password/', payload, format='json')
        self.assertEqual(response.status_code, 400)

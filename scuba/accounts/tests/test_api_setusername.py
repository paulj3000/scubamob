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


class APISetUsername(TestCase):
    @staticmethod
    def create_test_user(username='someuser', email='foo@nowhere.com'):
        return User.objects.create(
            first_name='First',
            last_name='Last',
            username=username,
            email=email)

    def test_set_good_username(self):
        """
        Test setting a good username
        """
        user = self.create_test_user()

        client = APIClient()
        client.force_authenticate(user=user)
        new_username = 'ausernamefoo'

        payload = {
            'username': new_username
        }

        response = client.put('/api/signup/username/', payload, format='json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['username'], new_username)

    def test_set_bad_username(self):
        """
        Test setting bad password
        """

        new_username = 'alreadyregistered'
        user = self.create_test_user()
        user2 = self.create_test_user(new_username, 'foo2@nowhere.com')

        user2.username = new_username

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'username': new_username
        }

        response = client.put('/api/signup/username/', payload, format='json')
        self.assertEquals(response.status_code, 400)
        print(response.json())
        print(response.json())
        print(response.json())
        print(response.json())

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


class TestUserLoginAPI(TestCase):
    @staticmethod
    def create_test_user(email='foo@nowhere.com'):
        user = User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-01-01',
            email=email)
        user.set_password('password')
        user.save()
        return user

    def test_login_user_1(self):
        """
        Test simple create user
        """
        user = TestUserLoginAPI.create_test_user()
        client = APIClient()
        payload = {
            'password': 'password',
            'email': 'foo@nowhere.com'
        }

        response = client.post('/api/login/', payload, format='json')

        id = response.json().get('id')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('first_name'), 'First')
        self.assertEqual(response.json().get('last_name'), 'Last')
        self.assertEqual(len(id), 32)
        self.assertNotIn('-', id)

        # check the login stuff, make sure there is one login
        self.assertEqual(len(user.get_all_logins()), 1)

        # make sure the login stuff is logged
        user_login = user.get_all_logins()[0]
        self.assertEqual(user_login.device, 'mobile')
        self.assertEqual(user_login.ip_address, '0.0.0.0')

    def test_login_user_2(self):
        """
        Test simple create user
        """
        user = TestUserLoginAPI.create_test_user()
        client = APIClient()
        payload = {
            'email': 'foo@nowhere.com',
            'password': 'password',
            'ip_address': '192.168.0.1',
            'device': 'some_mobile_device',
        }

        response = client.post('/api/login/', payload, format='json')
        self.assertEqual(response.status_code, 200)

        # check the login stuff, make sure there is one login
        self.assertEqual(len(user.get_all_logins()), 1)

        # make sure the login stuff is logged
        user_login = user.get_all_logins()[0]
        self.assertEqual(user_login.device, 'some_mobile_device')
        self.assertEqual(user_login.ip_address, '192.168.0.1')

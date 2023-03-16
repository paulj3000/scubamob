"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient


class TestUserLogin(TestCase):
    @staticmethod
    def create_test_user(username='someuser', email='foo@nowhere.com'):
        user = User.objects.create(
            first_name='First',
            last_name='Last',
            username=username,
            email=email)
        user.set_password('password')
        return user

    def test_login_user_1(self):
        """
        Test simple create user
        """
        user = TestUserLogin.create_test_user()
        client = APIClient()
        payload = {
            'username': 'someuser',
            'password': 'password,
        }

        response = client.post('/api/login/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('first_name'), 'first')
        self.assertEqual(response.json().get('last_name'), 'last')
        self.assertEqual(response.json().get('username'), 'someuserx')

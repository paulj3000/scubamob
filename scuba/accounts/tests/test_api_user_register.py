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


class TestUserRegisterAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_user_register_good(self):
        """
        Test good register signup
        """
        client = APIClient()
        payload = {
            'first_name': 'good',
            'last_name': 'user',
            'password': 'password',
            'email': 'goodsignup@nowhere.com',
            'username': 'goodsignup'
        }

        response = client.post('/api/register/', payload, format='json')
        id = response.json().get('id')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('username'), 'goodsignup')
        self.assertEqual(response.json().get('first_name'), 'good')
        self.assertEqual(response.json().get('last_name'), 'user')
        self.assertIsNotNone(response.json().get('profile_image'))
        self.assertEqual(len(id), 32)
        self.assertNotIn('-', id)

    def test_user_register_duplicate_email(self):
        """
        Test good register signup
        """
        client = APIClient()
        payload = {
            'first_name': 'foo',
            'last_name': 'user',
            'password': 'password',
            'email': 'foo@nowhere.com',
            'username': 'duplicateemail'
        }

        response = client.post('/api/register/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json().get('email'))
        self.assertEqual(response.json().get('email')[0], 'Email address foo@nowhere.com is already registered')

    def test_user_register_duplicate_username(self):
        """
        Test good register signup
        """
        client = APIClient()
        payload = {
            'first_name': 'foo',
            'last_name': 'user',
            'password': 'password',
            'email': 'dup@nowhere.com',
            'username': 'testuser3'
        }

        response = client.post('/api/register/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json().get('username'))
        self.assertEqual(response.json().get('username')[0], 'Username testuser3 is already registered')

    def test_user_register_short_username(self):
        """
        Test a short username
        """
        client = APIClient()

        for i in range(1, 5):
            username = 'x' * i
            payload = {
                'first_name': 'foo',
                'last_name': 'user',
                'password': 'password',
                'email': 'dup@nowhere.com',
                'username': username
            }

            response = client.post('/api/register/', payload, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertIsNotNone(response.json().get('username'))
            self.assertEqual(response.json().get('username')[0], f'Username {username} is an invalid length')

    def test_user_register_long_username(self):
        """
        Test a short username
        """
        client = APIClient()

        username = 'x' * 41
        payload = {
            'first_name': 'foo',
            'last_name': 'user',
            'password': 'password',
            'email': 'dup@nowhere.com',
            'username': username
        }

        response = client.post('/api/register/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json().get('username'))
        self.assertEqual(response.json().get('username')[0], f'Username {username} is an invalid length')

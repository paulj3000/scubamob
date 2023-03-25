"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient


class TestCreateUserAPI(TestCase):
    def test_create_user_1(self):
        """
        Test simple create user
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'date_of_birth': "1980-10-31",
            'password': "someweirdpassword",
            'email': "foo@nowhere.com"
        }

        response = client.post('/api/signup/createuser/', payload, format='json')

        id = response.json().get('id')
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(id)
        self.assertEqual(len(id), 32)
        self.assertNotIn('-', id)
        self.assertIsNotNone(response.json().get('profile_image'))
        self.assertEqual(response.json().get('first_name'), 'first')
        self.assertEqual(response.json().get('last_name'), 'last')
        self.assertEqual(response.json().get('setup_complete'), False)
        self.assertEqual(len(response.json().get('token')), 40)

    def test_create_user_duplicate_email(self):
        """
        Test email address cannot be a duplicate
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "someweirdpassword",
            'date_of_birth': "1980-10-31",
            'email': "foo@nowhere.com"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_create_user_coppa(self):
        """
        Test user has to be at least 13 years old
        """
        twelve_years_ago = (datetime.now() - relativedelta(years=12)).strftime("%Y-%m-%d")
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "somewoorirdpass",
            'date_of_birth': twelve_years_ago,
            'email': "foo@nowhere.com"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('date_of_birth', response.json())

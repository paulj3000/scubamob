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


class TestProfileAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_profile(self):
        """
        Test account profile
        """
        user = User.objects.get(email='foo@nowhere.com')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/profile/', format='json')
        self.assertEqual(response.status_code, 200)

        user_json = response.json()
        self.assertIn('profile', user_json)
        self.assertIn('id', user_json['profile'])
        self.assertIn('buddies_count', user_json['profile'])
        self.assertIn('profile_image', user_json['profile'])
        self.assertEqual(user_json['profile'].get('full_name'), 'First Last')

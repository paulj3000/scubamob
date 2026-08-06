"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class APISetPassword(TestCase):
    fixtures = ["test_users.json"]

    def test_set_good_password(self):
        """
        Test setting good password
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'password': "ThisisAGoodPassword%",
        }

        response = client.put('/api/signup/password/', payload, format='json')
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.check_password('ThisisAGoodPassword%'))

    def test_set_bad_password(self):
        """
        Test setting bad password
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'password': "xxx",
        }

        response = client.put('/api/signup/password/', payload, format='json')
        self.assertEqual(response.status_code, 400)

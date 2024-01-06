"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient


class TestPasswordApi(TestCase):
    fixtures = ["test_users.json"]

    def test_good_email(self):
        """
        Test me account profile
        """
        # make sure the user has to be logged in
        to_send = {
            'email': 'good@email.com',
        }

        client = APIClient()
        response = client.post('/api/password/reset/', to_send, format='json')
        self.assertEqual(response.status_code, 200)

    def test_bad_email(self):
        """
        Test me account profile
        """
        # make sure the user has to be logged in
        to_send = {
            'email': 'bad_email.com',
        }

        client = APIClient()
        response = client.post('/api/password/reset/', to_send, format='json')
        self.assertEqual(response.status_code, 400)

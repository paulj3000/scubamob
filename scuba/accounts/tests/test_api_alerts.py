"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
from unittest import mock

import requests
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestAlertsAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_alerts_returns_canned_response_in_test_mode(self):
        """
        Test that the alerts endpoint short-circuits to a canned response
        when IS_TEST is set, without calling the alerting server
        """
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        with mock.patch.dict(os.environ, {'IS_TEST': 'true'}):
            response = client.get('/api/accounts/alerts', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'alerts': []})

    def test_alerts_returns_error_when_alerting_server_unreachable(self):
        """
        Test that the alerts endpoint returns a 500 when the alerting server
        cannot be reached
        """
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        with mock.patch.dict(os.environ, {'IS_TEST': ''}), \
                mock.patch('scuba.accounts.apis.socket.requests.get',
                           side_effect=requests.exceptions.ConnectionError):
            response = client.get('/api/accounts/alerts', format='json')

        self.assertEqual(response.status_code, 500)

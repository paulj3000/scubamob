"""
Tests for AlertsApi (scuba.accounts.apis.socket). Covers the
ALERT_SERVER_ACTIVE settings-based gate -- previously the 200/400 split
accidentally hinged on whether a never-configured sitesettings.SystemApi
row existed, not on this flag at all (see MODERNIZATION_ROADMAP.md item 9).
"""
import os
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestAlertsAPI(TestCase):
    fixtures = ["test_users.json"]

    @patch('scuba.accounts.apis.socket.ALERT_SERVER_ACTIVE', True)
    def test_alert_server_active_is_active(self):
        """
        Test if the alerting server is active
        """
        os.environ['IS_TEST'] = "true"

        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/alerts', format='json')
        self.assertEqual(response.status_code, 200)

    @patch('scuba.accounts.apis.socket.ALERT_SERVER_ACTIVE', False)
    def test_alert_server_active_is_inactive(self):
        """
        Test if the alerting server is active
        """
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/alerts', format='json')
        self.assertEqual(response.status_code, 400)

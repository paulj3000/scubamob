"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.sitesettings.models import SystemSetting, SystemApi


class TestAlertsAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_alert_server_active_is_active(self):
        """
        Test if the alerting server is active
        """
        os.environ['IS_TEST'] = "true"

        SystemSetting.objects.update_or_create(key='ALERT_SERVER_ACTIVE',
                                               defaults={'value': 1})

        SystemApi.objects.update_or_create(key='ALERTING_URL',
                                               defaults={'value': 'xxx'})
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/alerts', format='json')
        self.assertEqual(response.status_code, 200)

    def test_alert_server_active_is_inactive(self):
        """
        Test if the alerting server is active
        """
        _, __ = SystemSetting.objects.update_or_create(key='ALERT_SERVER_ACTIVE',
                                                       defaults={'value': 0})
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/alerts', format='json')
        self.assertEqual(response.status_code, 400)

    def test_alert_server_active_is_inactive_2(self):
        """
        Test if the alerting server is active
        """
        _, __ = SystemSetting.objects.update_or_create(key='ALERT_SERVER_ACTIVE',
                                                       defaults={'value': 'false'})
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/alerts', format='json')
        self.assertEqual(response.status_code, 400)

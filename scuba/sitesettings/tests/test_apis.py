"""
Tests for scuba.sitesettings.apis (CODE_REVIEW.md §5 sitesettings
findings): GetSystemEndpointsApi called a nonexistent
Endpoint.get_active_endpoints(), and GetSystemSettingsApi's non-/all
branch referenced item.url on SystemApi, a model with no url field
(the real field is value). Both were public, unauthenticated routes
guaranteed to 500 on every call.

GetSystemSettingsApi (both the key-filtered and /all variants) is now
IsAuthenticated: its /all branch used to expose the entire SystemApi
table (internal AWS/billing/chat/alerting server URLs) to anonymous
callers, and no first-party template/JS in this repo ever called it
unauthenticated (Known Technical Debt, resolved).
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.sitesettings.models import Endpoint, SystemApi


class TestGetSystemEndpointsApi(TestCase):
    def test_returns_only_active_endpoints(self):
        system = SystemApi.objects.create(key='CHAT_SERVER', value='http://chat.test')
        Endpoint.objects.create(
            system=system, key='ACTIVE_ENDPOINT', url='/active', verb='GET', is_active=True)
        Endpoint.objects.create(
            system=system, key='INACTIVE_ENDPOINT', url='/inactive', verb='GET',
            is_active=False)

        client = APIClient()
        response = client.get('/api/endpoints', format='json')

        self.assertEqual(response.status_code, 200)
        endpoints = response.json()['endpoints']
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['key'], 'ACTIVE_ENDPOINT')


class TestGetSystemSettingsApi(TestCase):
    fixtures = ["test_users.json"]

    def test_requires_authentication(self):
        SystemApi.objects.create(key='CHAT_SERVER', value='http://chat.test', is_active=True)

        client = APIClient()
        response = client.get(
            '/api/sitesettings', {'key': ['CHAT_SERVER']}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_all_variant_requires_authentication(self):
        SystemApi.objects.create(key='CHAT_SERVER', value='http://chat.test', is_active=True)

        client = APIClient()
        response = client.get('/api/sitesettings/all', format='json')

        self.assertEqual(response.status_code, 401)

    def test_returns_the_requested_keys_values(self):
        SystemApi.objects.create(key='CHAT_SERVER', value='http://chat.test', is_active=True)
        SystemApi.objects.create(
            key='SETTINGS_SERVER', value='http://settings.test', is_active=True)

        user = User.objects.get(email='foo@nowhere.com')
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(
            '/api/sitesettings', {'key': ['CHAT_SERVER']}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['apis'], {'CHAT_SERVER': 'http://chat.test'})

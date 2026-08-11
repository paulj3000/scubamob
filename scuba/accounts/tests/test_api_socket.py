"""
Tests for SocketApi (scuba.accounts.apis.socket). Previously it built its
'server' payload from sitesettings.SystemApi rows for three keys
(SOCKET_SERVER_ACTIVE, SOCKET_SERVER_URL, CHAT_SERVER), only one of which
(CHAT_SERVER) ever had a real fixture value -- now it reads settings.CHAT_SERVER
directly (see MODERNIZATION_ROADMAP.md item 9).
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.settings import CHAT_SERVER


class TestSocketApi(TestCase):
    fixtures = ["test_users.json"]

    def test_socket_api_returns_the_chat_server_setting(self):
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/socket', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['socket']['server'], {'CHAT_SERVER': CHAT_SERVER})

"""
Tests for SocketApi (scuba.accounts.apis.socket). Previously it advertised a
'server' payload pointing at the legacy external CHAT_SERVER; that server
was retired along with the rest of the CHAT_SERVER-based chat code (see
docs/chat_dynamo.md), so the response now only carries basic user info.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestSocketApi(TestCase):
    fixtures = ["test_users.json"]

    def test_socket_api_returns_basic_user_info(self):
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/accounts/socket', format='json')

        self.assertEqual(response.status_code, 200)
        socket_data = response.json()['socket']
        self.assertEqual(socket_data['user']['id'], str(user.id))
        self.assertNotIn('server', socket_data)

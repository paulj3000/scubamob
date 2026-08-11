"""
Lightweight coverage confirming outbound requests.get/post calls set a
timeout (CODE_REVIEW.md §3 item 14). URL-building helpers and requests
itself are mocked -- these tests only verify the timeout kwarg is set,
not real network behavior; no live external service is touched.
"""
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestChatApisTimeouts(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='chattimeout@nowhere.com', username='chattimeoutuser',
            password='tester1234', first_name='Chat', last_name='User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('scuba.accounts.apis.chat.requests.get')
    @patch('scuba.accounts.apis.chat.CHAT_SERVER', 'http://chat.test')
    def test_chat_w_user_api_get_has_a_timeout(self, mock_get):
        mock_get.return_value.json.return_value = {'chat': None}

        self.client.get('/api/accounts/chats/', format='json')

        self.assertEqual(mock_get.call_args.kwargs.get('timeout'), 5)

    @patch('scuba.accounts.apis.chat.requests.get')
    @patch('scuba.accounts.apis.chat.CHAT_SERVER', 'http://chat.test')
    def test_get_chats_api_has_a_timeout(self, mock_get):
        mock_get.return_value.json.return_value = {}

        self.client.get('/api/chats/', format='json')

        self.assertEqual(mock_get.call_args.kwargs.get('timeout'), 5)

    @patch('scuba.accounts.apis.chat.requests.get')
    @patch('scuba.accounts.apis.chat.CHAT_SERVER', 'http://chat.test')
    def test_get_all_chats_api_has_a_timeout(self, mock_get):
        mock_get.return_value.json.return_value = {}

        self.client.get('/api/chats/all', format='json')

        self.assertEqual(mock_get.call_args.kwargs.get('timeout'), 5)

    @patch('scuba.accounts.serializers.chat.requests.post')
    @patch('scuba.accounts.serializers.chat.CHAT_SERVER', 'http://chat.test')
    def test_chat_serializer_save_has_a_timeout(self, mock_post):
        other = User.objects.create_user(
            email='chatother@nowhere.com', username='chatotheruser', password='tester1234',
            first_name='Other', last_name='User')
        mock_post.return_value.json.return_value = {'chat': {}}

        self.client.post('/api/accounts/chats/', {'users': [other.pk_as_str]}, format='json')

        self.assertEqual(mock_post.call_args.kwargs.get('timeout'), 5)


class TestSettingsApisTimeouts(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='settingstimeout@nowhere.com', username='settingstimeoutuser',
            password='tester1234', first_name='Settings', last_name='User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('scuba.accounts.apis.settings.requests.get')
    @patch('scuba.accounts.apis.settings.SETTINGS_SERVER', 'http://settings.test')
    def test_user_setting_api_get_has_a_timeout(self, mock_get):
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.status_code = 200

        self.client.get('/api/settings/list/options', {'settings': 'dark-mode'}, format='json')

        self.assertEqual(mock_get.call_args.kwargs.get('timeout'), 5)

    @patch('scuba.accounts.apis.settings.requests.post')
    @patch('scuba.accounts.apis.settings.SETTINGS_SERVER', 'http://settings.test')
    def test_user_setting_api_post_has_a_timeout(self, mock_post):
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200

        self.client.post('/api/settings/list/options', {'dark-mode': 1}, format='json')

        self.assertEqual(mock_post.call_args.kwargs.get('timeout'), 5)

    @patch('scuba.accounts.apis.settings.requests.get')
    @patch('scuba.accounts.apis.settings.SETTINGS_SERVER', 'http://settings.test')
    def test_user_setting_list_api_get_has_a_timeout(self, mock_get):
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.status_code = 200

        self.client.get('/api/settings/list', {'settings': 'dark-mode'}, format='json')

        self.assertEqual(mock_get.call_args.kwargs.get('timeout'), 5)

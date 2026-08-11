from django.apps import apps
from django.test import SimpleTestCase


class TestChatAppConfig(SimpleTestCase):
    def test_chat_app_is_installed(self):
        config = apps.get_app_config('chat')
        self.assertEqual(config.name, 'scuba.chat')

"""
No real Redis connection ever happens here -- redis.Redis.from_url is
mocked at the module boundary, same pattern test_infrastructure_dynamodb.py
uses for boto3.
"""
from unittest.mock import patch

from django.test import SimpleTestCase

from scuba.chat.infrastructure import redis as redis_infra
from scuba.settings import CHAT_REDIS_URL


class TestGetClient(SimpleTestCase):
    @patch('scuba.chat.infrastructure.redis.redis.Redis.from_url')
    def test_get_client_uses_the_configured_url(self, mock_from_url):
        redis_infra.get_client()

        mock_from_url.assert_called_once_with(CHAT_REDIS_URL)

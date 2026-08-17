"""
No real AWS call ever happens here -- get_session is mocked at the module
boundary, same pattern test_infrastructure_dynamodb.py uses.
"""
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from scuba.chat.infrastructure import s3


class TestGetClient(SimpleTestCase):
    @patch('scuba.chat.infrastructure.s3.get_session')
    def test_get_client_returns_a_low_level_s3_client(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        s3.get_client()

        mock_session.client.assert_called_once_with('s3', config=s3._CLIENT_CONFIG)

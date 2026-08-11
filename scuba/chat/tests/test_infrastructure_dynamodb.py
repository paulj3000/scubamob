"""
No real AWS call ever happens here -- get_session is mocked at the module
boundary, same pattern scuba.libs.aws.s3's tests already use.
"""
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from scuba.chat.infrastructure import dynamodb
from scuba.settings import CHAT_DYNAMODB_TABLE


class TestGetTable(SimpleTestCase):
    @patch('scuba.chat.infrastructure.dynamodb.get_session')
    def test_get_table_defaults_to_the_configured_table(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        dynamodb.get_table()

        mock_session.resource.assert_called_once_with('dynamodb')
        mock_session.resource.return_value.Table.assert_called_once_with(CHAT_DYNAMODB_TABLE)

    @patch('scuba.chat.infrastructure.dynamodb.get_session')
    def test_get_table_accepts_an_explicit_table_name(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        dynamodb.get_table('other-table')

        mock_session.resource.return_value.Table.assert_called_once_with('other-table')

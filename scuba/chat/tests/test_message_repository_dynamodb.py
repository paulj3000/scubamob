"""
DynamoDBMessageRepository (docs/chat_dynamo.md §15, Phase 2). No real AWS
call ever happens here -- get_table is mocked at the module boundary,
same pattern scuba.libs.aws.s3's and this app's own
test_infrastructure_dynamodb.py tests already use.
"""
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.utils import timezone

from scuba.chat.domain import Message, MessageType, generate_message_id
from scuba.chat.exceptions import MessageNotFoundError
from scuba.chat.repositories.message_repository import DynamoDBMessageRepository, _message_to_item


def _make_message(conversation_id='conv1', **kwargs):
    defaults = dict(
        message_id=generate_message_id(),
        conversation_id=conversation_id,
        sender_id='user1',
        message_type=MessageType.TEXT,
        body='hello',
        created_at=timezone.now(),
    )
    defaults.update(kwargs)
    return Message(**defaults)


@patch('scuba.chat.repositories.message_repository.get_table')
class TestDynamoDBMessageRepository(SimpleTestCase):
    def setUp(self):
        self.repo = DynamoDBMessageRepository()

    def test_create_message_calls_put_item_with_the_expected_item_shape(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        message = _make_message()

        result = self.repo.create_message(message)

        mock_table.put_item.assert_called_once()
        item = mock_table.put_item.call_args.kwargs['Item']
        self.assertEqual(item['PK'], f'CONVERSATION#{message.conversation_id}')
        self.assertEqual(item['message_id'], message.message_id)
        self.assertEqual(item['body'], message.body)
        self.assertIs(result, message)

    def test_create_message_is_idempotent_on_client_message_id(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        existing = _make_message(client_message_id='retry-key-1')
        mock_table.query.return_value = {'Items': [_message_to_item(existing)]}

        retry = _make_message(client_message_id='retry-key-1', body='should be ignored')
        result = self.repo.create_message(retry)

        self.assertEqual(result.message_id, existing.message_id)
        self.assertEqual(result.body, 'hello')
        mock_table.put_item.assert_not_called()

    def test_get_message_returns_none_when_missing(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': []}

        self.assertIsNone(self.repo.get_message('conv1', 'nope'))

    def test_get_message_returns_the_matching_message(self, mock_get_table):
        message = _make_message()
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': [_message_to_item(message)]}

        found = self.repo.get_message(message.conversation_id, message.message_id)

        self.assertEqual(found.message_id, message.message_id)
        self.assertEqual(found.body, message.body)

    def test_list_messages_returns_a_cursor_when_more_pages_remain(self, mock_get_table):
        message = _make_message()
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        last_key = {'PK': 'CONVERSATION#conv1', 'SK': 'MESSAGE#x#y'}
        mock_table.query.return_value = {
            'Items': [_message_to_item(message)],
            'LastEvaluatedKey': last_key,
        }

        messages, cursor = self.repo.list_messages('conv1', limit=1)

        self.assertEqual(len(messages), 1)
        self.assertIsNotNone(cursor)

        mock_table.query.return_value = {'Items': []}
        self.repo.list_messages('conv1', limit=1, cursor=cursor)
        self.assertEqual(
            mock_table.query.call_args.kwargs['ExclusiveStartKey'], last_key)

    def test_list_messages_no_cursor_on_the_last_page(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': []}

        messages, cursor = self.repo.list_messages('conv1')

        self.assertEqual(messages, [])
        self.assertIsNone(cursor)

    def test_update_message_sets_body_and_edited_at(self, mock_get_table):
        message = _make_message()
        item = _message_to_item(message)
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': [item]}

        updated = self.repo.update_message(
            message.conversation_id, message.message_id, body='edited')

        self.assertEqual(updated.body, 'edited')
        self.assertIsNotNone(updated.edited_at)
        mock_table.update_item.assert_called_once_with(
            Key={'PK': item['PK'], 'SK': item['SK']},
            UpdateExpression='SET body = :body, edited_at = :edited_at',
            ExpressionAttributeValues={
                ':body': 'edited', ':edited_at': updated.edited_at.isoformat()},
        )

    def test_update_message_raises_when_missing(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': []}

        with self.assertRaises(MessageNotFoundError):
            self.repo.update_message('conv1', 'nope', body='x')

    def test_soft_delete_sets_deleted_at(self, mock_get_table):
        message = _make_message()
        item = _message_to_item(message)
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': [item]}

        deleted = self.repo.soft_delete_message(message.conversation_id, message.message_id)

        self.assertIsNotNone(deleted.deleted_at)
        mock_table.update_item.assert_called_once_with(
            Key={'PK': item['PK'], 'SK': item['SK']},
            UpdateExpression='SET deleted_at = :deleted_at',
            ExpressionAttributeValues={':deleted_at': deleted.deleted_at.isoformat()},
        )

    def test_soft_delete_raises_when_missing(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        mock_table.query.return_value = {'Items': []}

        with self.assertRaises(MessageNotFoundError):
            self.repo.soft_delete_message('conv1', 'nope')

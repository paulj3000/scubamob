"""
Exercises DynamoDBMessageRepository against moto's in-process fake
DynamoDB -- real boto3 query/put/transact_write_items calls, but no live
AWS and no Docker/network dependency (CLAUDE.md forbids tests depending
on a live external service).
"""
from datetime import timedelta
from unittest import mock

import boto3
from django.test import SimpleTestCase
from django.utils import timezone
from moto import mock_aws

from scuba.chat.domain import Message, MessageType, generate_message_id
from scuba.chat.exceptions import MessageNotFoundError
from scuba.chat.repositories.message_repository import DynamoDBMessageRepository
from scuba.settings import CHAT_DYNAMODB_REGION, CHAT_DYNAMODB_TABLE


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


@mock_aws
class TestDynamoDBMessageRepository(SimpleTestCase):
    """ SimpleTestCase: no Django DB needed, only DynamoDB (via moto). """

    def setUp(self):
        env_patcher = mock.patch.dict(
            'os.environ', {'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing'})
        env_patcher.start()
        self.addCleanup(env_patcher.stop)

        client = boto3.client('dynamodb', region_name=CHAT_DYNAMODB_REGION)
        client.create_table(
            TableName=CHAT_DYNAMODB_TABLE,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'message_id', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[{
                'IndexName': 'MessageIdIndex',
                'KeySchema': [{'AttributeName': 'message_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
            }],
            BillingMode='PAY_PER_REQUEST',
        )
        self.repo = DynamoDBMessageRepository()

    def test_create_and_get_message(self):
        message = _make_message()
        self.repo.create_message(message)

        found = self.repo.get_message('conv1', message.message_id)

        self.assertEqual(found.message_id, message.message_id)
        self.assertEqual(found.body, 'hello')

    def test_get_message_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_message('conv1', 'nope'))

    def test_get_message_returns_none_for_the_wrong_conversation(self):
        message = _make_message(conversation_id='conv1')
        self.repo.create_message(message)

        self.assertIsNone(self.repo.get_message('conv2', message.message_id))

    def test_create_message_is_idempotent_on_client_message_id(self):
        first = _make_message(client_message_id='retry-key-1')
        self.repo.create_message(first)

        retry = _make_message(client_message_id='retry-key-1', body='should be ignored')
        result = self.repo.create_message(retry)

        self.assertEqual(result.message_id, first.message_id)
        self.assertEqual(result.body, 'hello')
        messages, _ = self.repo.list_messages('conv1')
        self.assertEqual(len(messages), 1)

    def test_get_message_by_client_id_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_message_by_client_id('conv1', 'nope'))

    def test_get_message_by_client_id_finds_the_claimed_message(self):
        message = _make_message(client_message_id='retry-key-1')
        self.repo.create_message(message)

        found = self.repo.get_message_by_client_id('conv1', 'retry-key-1')

        self.assertEqual(found.message_id, message.message_id)

    def test_list_messages_orders_chronologically_and_paginates(self):
        now = timezone.now()
        for i in range(3):
            self.repo.create_message(_make_message(created_at=now + timedelta(seconds=i)))

        page_one, cursor = self.repo.list_messages('conv1', limit=2)
        self.assertEqual(len(page_one), 2)
        self.assertLess(page_one[0].created_at, page_one[1].created_at)
        self.assertIsNotNone(cursor)

        page_two, cursor_two = self.repo.list_messages('conv1', limit=2, cursor=cursor)
        self.assertEqual(len(page_two), 1)
        self.assertIsNone(cursor_two)

    def test_update_message_sets_body_and_edited_at(self):
        message = _make_message()
        self.repo.create_message(message)

        updated = self.repo.update_message('conv1', message.message_id, body='edited')

        self.assertEqual(updated.body, 'edited')
        self.assertIsNotNone(updated.edited_at)

    def test_update_message_raises_when_missing(self):
        with self.assertRaises(MessageNotFoundError):
            self.repo.update_message('conv1', 'nope', body='x')

    def test_soft_delete_sets_deleted_at_without_removing_the_item(self):
        message = _make_message()
        self.repo.create_message(message)

        deleted = self.repo.soft_delete_message('conv1', message.message_id)

        self.assertIsNotNone(deleted.deleted_at)
        self.assertIsNotNone(self.repo.get_message('conv1', message.message_id))

    def test_soft_delete_raises_when_missing(self):
        with self.assertRaises(MessageNotFoundError):
            self.repo.soft_delete_message('conv1', 'nope')

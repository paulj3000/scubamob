"""
Exercises DynamoDBAttachmentRepository and S3AttachmentStorage against
moto's in-process fakes -- real boto3 put/query/put_object/
generate_presigned_url calls, but no live AWS and no Docker/network
dependency (CLAUDE.md forbids tests depending on a live external service).
"""
from datetime import timedelta
from unittest import mock

import boto3
from django.test import SimpleTestCase
from django.utils import timezone
from moto import mock_aws

from scuba.chat.domain import Attachment, AttachmentType, generate_attachment_id
from scuba.chat.repositories.attachment_repository import (
    ATTACHMENT_ID_INDEX, DynamoDBAttachmentRepository, S3AttachmentStorage,
)
from scuba.settings import CHAT_ATTACHMENT_BUCKET, CHAT_DYNAMODB_REGION, CHAT_DYNAMODB_TABLE


def _make_attachment(conversation_id='conv1', message_id='msg1', **kwargs):
    defaults = dict(
        attachment_id=generate_attachment_id(),
        conversation_id=conversation_id,
        message_id=message_id,
        attachment_type=AttachmentType.IMAGE,
        s3_key=f"chat/{conversation_id}/{message_id}/attachment.jpg",
        content_type='image/jpeg',
        size=1024,
        created_at=timezone.now(),
    )
    defaults.update(kwargs)
    return Attachment(**defaults)


@mock_aws
class TestDynamoDBAttachmentRepository(SimpleTestCase):
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
                {'AttributeName': 'attachment_id', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[{
                'IndexName': ATTACHMENT_ID_INDEX,
                'KeySchema': [{'AttributeName': 'attachment_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
            }],
            BillingMode='PAY_PER_REQUEST',
        )
        self.repo = DynamoDBAttachmentRepository()

    def test_create_and_get_attachment(self):
        attachment = _make_attachment()
        self.repo.create_attachment(attachment)

        found = self.repo.get_attachment('conv1', attachment.attachment_id)

        self.assertEqual(found.attachment_id, attachment.attachment_id)
        self.assertEqual(found.s3_key, attachment.s3_key)
        self.assertEqual(found.size, attachment.size)

    def test_get_attachment_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_attachment('conv1', 'nope'))

    def test_get_attachment_returns_none_for_the_wrong_conversation(self):
        attachment = _make_attachment(conversation_id='conv1')
        self.repo.create_attachment(attachment)

        self.assertIsNone(self.repo.get_attachment('conv2', attachment.attachment_id))

    def test_list_attachments_for_message_only_returns_that_messages_attachments(self):
        now = timezone.now()
        first = _make_attachment(message_id='msg1', created_at=now)
        second = _make_attachment(message_id='msg1', created_at=now + timedelta(seconds=1))
        other_message = _make_attachment(message_id='msg2', created_at=now)
        self.repo.create_attachment(first)
        self.repo.create_attachment(second)
        self.repo.create_attachment(other_message)

        attachments = self.repo.list_attachments_for_message('conv1', 'msg1')

        self.assertEqual(
            {a.attachment_id for a in attachments}, {first.attachment_id, second.attachment_id})


@mock_aws
class TestS3AttachmentStorage(SimpleTestCase):
    def setUp(self):
        env_patcher = mock.patch.dict(
            'os.environ', {'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing'})
        env_patcher.start()
        self.addCleanup(env_patcher.stop)

        boto3.client('s3', region_name='us-east-1').create_bucket(Bucket=CHAT_ATTACHMENT_BUCKET)
        self.storage = S3AttachmentStorage()

    def test_upload_stores_the_object_in_the_configured_bucket(self):
        self.storage.upload('chat/conv1/msg1/att1.jpg', b'file-bytes', content_type='image/jpeg')

        client = boto3.client('s3', region_name='us-east-1')
        obj = client.get_object(Bucket=CHAT_ATTACHMENT_BUCKET, Key='chat/conv1/msg1/att1.jpg')
        self.assertEqual(obj['Body'].read(), b'file-bytes')
        self.assertEqual(obj['ContentType'], 'image/jpeg')

    def test_get_download_url_returns_a_signed_url(self):
        self.storage.upload('chat/conv1/msg1/att1.jpg', b'file-bytes', content_type='image/jpeg')

        url = self.storage.get_download_url('chat/conv1/msg1/att1.jpg', expires_in=60)

        self.assertIn(CHAT_ATTACHMENT_BUCKET, url)
        self.assertIn('chat/conv1/msg1/att1.jpg', url)
        self.assertIn('X-Amz-Signature', url)

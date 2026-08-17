from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from scuba.chat.domain import (
    Attachment, AttachmentType, Message, MessageType, generate_attachment_id, generate_message_id,
)
from scuba.chat.exceptions import MessageNotFoundError
from scuba.chat.repositories.attachment_repository import (
    AttachmentRepository, AttachmentStorage, InMemoryAttachmentRepository, InMemoryAttachmentStorage,
)
from scuba.chat.repositories.conversation_repository import ConversationRepository
from scuba.chat.repositories.message_repository import InMemoryMessageRepository, MessageRepository
from scuba.chat.repositories.notification_repository import NotificationRepository
from scuba.chat.repositories.participant_repository import ParticipantRepository
from scuba.chat.repositories.reaction_repository import ReactionRepository


class TestRepositoryInterfacesAreAbstract(SimpleTestCase):
    """ Every *Repository interface must stay uninstantiable on its own. """

    def test_cannot_instantiate_message_repository_directly(self):
        with self.assertRaises(TypeError):
            MessageRepository()

    def test_cannot_instantiate_conversation_repository_directly(self):
        with self.assertRaises(TypeError):
            ConversationRepository()

    def test_cannot_instantiate_participant_repository_directly(self):
        with self.assertRaises(TypeError):
            ParticipantRepository()

    def test_cannot_instantiate_reaction_repository_directly(self):
        with self.assertRaises(TypeError):
            ReactionRepository()

    def test_cannot_instantiate_attachment_repository_directly(self):
        with self.assertRaises(TypeError):
            AttachmentRepository()

    def test_cannot_instantiate_notification_repository_directly(self):
        with self.assertRaises(TypeError):
            NotificationRepository()

    def test_cannot_instantiate_attachment_storage_directly(self):
        with self.assertRaises(TypeError):
            AttachmentStorage()


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


class TestInMemoryMessageRepository(SimpleTestCase):
    """
    Exercises the MessageRepository interface end to end without any real
    DynamoDB -- this fake is the Phase 0 "local/test strategy" (docs/
    chat_dynamo.md §58), and Phase 2's real boto3-backed implementation
    must satisfy the exact same behavior.
    """

    def setUp(self):
        self.repo = InMemoryMessageRepository()

    def test_create_and_get_message(self):
        message = _make_message()
        self.repo.create_message(message)

        found = self.repo.get_message('conv1', message.message_id)

        self.assertEqual(found, message)

    def test_get_message_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_message('conv1', 'nope'))

    def test_create_message_is_idempotent_on_client_message_id(self):
        first = _make_message(client_message_id='retry-key-1')
        self.repo.create_message(first)

        retry = _make_message(client_message_id='retry-key-1', body='should be ignored')
        result = self.repo.create_message(retry)

        self.assertEqual(result.message_id, first.message_id)
        self.assertEqual(result.body, 'hello')
        messages, _ = self.repo.list_messages('conv1')
        self.assertEqual(len(messages), 1)

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

    def test_soft_delete_sets_deleted_at_without_removing_the_message(self):
        message = _make_message()
        self.repo.create_message(message)

        deleted = self.repo.soft_delete_message('conv1', message.message_id)

        self.assertIsNotNone(deleted.deleted_at)
        self.assertIsNotNone(self.repo.get_message('conv1', message.message_id))

    def test_soft_delete_raises_when_missing(self):
        with self.assertRaises(MessageNotFoundError):
            self.repo.soft_delete_message('conv1', 'nope')


def _make_attachment(conversation_id='conv1', message_id='msg1', **kwargs):
    defaults = dict(
        attachment_id=generate_attachment_id(),
        conversation_id=conversation_id,
        message_id=message_id,
        attachment_type=AttachmentType.IMAGE,
        s3_key='chat/conv1/msg1/attachment.jpg',
        content_type='image/jpeg',
        size=1024,
        created_at=timezone.now(),
    )
    defaults.update(kwargs)
    return Attachment(**defaults)


class TestInMemoryAttachmentRepository(SimpleTestCase):
    def setUp(self):
        self.repo = InMemoryAttachmentRepository()

    def test_create_and_get_attachment(self):
        attachment = _make_attachment()
        self.repo.create_attachment(attachment)

        found = self.repo.get_attachment('conv1', attachment.attachment_id)

        self.assertEqual(found, attachment)

    def test_get_attachment_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_attachment('conv1', 'nope'))

    def test_list_attachments_for_message_only_returns_that_messages_attachments(self):
        first = _make_attachment(message_id='msg1')
        second = _make_attachment(message_id='msg1')
        other_message = _make_attachment(message_id='msg2')
        self.repo.create_attachment(first)
        self.repo.create_attachment(second)
        self.repo.create_attachment(other_message)

        attachments = self.repo.list_attachments_for_message('conv1', 'msg1')

        self.assertEqual({a.attachment_id for a in attachments}, {first.attachment_id, second.attachment_id})


class TestInMemoryAttachmentStorage(SimpleTestCase):
    def setUp(self):
        self.storage = InMemoryAttachmentStorage()

    def test_upload_stores_the_bytes_under_the_given_key(self):
        self.storage.upload('key1', b'file-bytes', content_type='image/jpeg')

        self.assertEqual(self.storage.objects['key1'], b'file-bytes')

    def test_get_download_url_returns_a_url_for_the_key(self):
        url = self.storage.get_download_url('key1', expires_in=60)

        self.assertIn('key1', url)

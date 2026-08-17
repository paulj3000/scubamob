from datetime import datetime, timezone as dt_timezone

from django.test import SimpleTestCase

from scuba.chat.domain import (
    Attachment, AttachmentType, Message, MessageType, attachment_sort_key, conversation_partition_key,
    generate_attachment_id, generate_message_id, message_sort_key, user_channel_group_name,
)


class TestMessageTypeAll(SimpleTestCase):
    def test_contains_every_declared_message_type(self):
        self.assertEqual(set(MessageType.ALL), {
            MessageType.TEXT, MessageType.SYSTEM, MessageType.DIVE, MessageType.DIVE_PLAN,
            MessageType.DIVE_SITE, MessageType.LOGBOOK_ENTRY, MessageType.EQUIPMENT,
            MessageType.MARKETPLACE_ITEM,
        })


class TestAttachmentTypeAll(SimpleTestCase):
    def test_contains_every_declared_attachment_type(self):
        self.assertEqual(set(AttachmentType.ALL), {AttachmentType.IMAGE, AttachmentType.DOCUMENT})


class TestGenerateMessageId(SimpleTestCase):
    def test_returns_a_32_character_hex_string(self):
        message_id = generate_message_id()
        self.assertEqual(len(message_id), 32)
        int(message_id, 16)  # raises ValueError if it isn't hex

    def test_generates_unique_ids(self):
        self.assertNotEqual(generate_message_id(), generate_message_id())


class TestGenerateAttachmentId(SimpleTestCase):
    def test_returns_a_32_character_hex_string(self):
        attachment_id = generate_attachment_id()
        self.assertEqual(len(attachment_id), 32)
        int(attachment_id, 16)  # raises ValueError if it isn't hex

    def test_generates_unique_ids(self):
        self.assertNotEqual(generate_attachment_id(), generate_attachment_id())


class TestKeyBuilders(SimpleTestCase):
    def test_conversation_partition_key(self):
        self.assertEqual(conversation_partition_key('abc123'), 'CONVERSATION#abc123')

    def test_user_channel_group_name(self):
        self.assertEqual(user_channel_group_name('abc123'), 'chat_user_abc123')

    def test_message_sort_key_includes_timestamp_and_id(self):
        created_at = datetime(2026, 8, 11, 14, 31, 12, tzinfo=dt_timezone.utc)

        key = message_sort_key(created_at, 'abc123')

        self.assertEqual(key, f"MESSAGE#{created_at.isoformat()}#abc123")

    def test_two_messages_in_the_same_millisecond_get_distinct_sort_keys(self):
        created_at = datetime(2026, 8, 11, 14, 31, 12, 182000, tzinfo=dt_timezone.utc)

        key_one = message_sort_key(created_at, generate_message_id())
        key_two = message_sort_key(created_at, generate_message_id())

        self.assertNotEqual(key_one, key_two)

    def test_attachment_sort_key_includes_message_and_attachment_id(self):
        key = attachment_sort_key('msg1', 'att1')

        self.assertEqual(key, 'ATTACHMENT#msg1#att1')


class TestMessageDataclass(SimpleTestCase):
    def test_optional_fields_default_to_none(self):
        message = Message(
            message_id='abc123',
            conversation_id='conv1',
            sender_id='user1',
            message_type=MessageType.TEXT,
            body='hello',
            created_at=datetime(2026, 8, 11, tzinfo=dt_timezone.utc),
        )

        self.assertIsNone(message.client_message_id)
        self.assertIsNone(message.edited_at)
        self.assertIsNone(message.deleted_at)
        self.assertIsNone(message.reply_to_message_id)
        self.assertIsNone(message.entity_type)
        self.assertIsNone(message.entity_id)


class TestAttachmentDataclass(SimpleTestCase):
    def test_original_filename_defaults_to_none(self):
        attachment = Attachment(
            attachment_id='att1',
            conversation_id='conv1',
            message_id='msg1',
            attachment_type=AttachmentType.IMAGE,
            s3_key='chat/conv1/msg1/att1.jpg',
            content_type='image/jpeg',
            size=1024,
            created_at=datetime(2026, 8, 11, tzinfo=dt_timezone.utc),
        )

        self.assertIsNone(attachment.original_filename)

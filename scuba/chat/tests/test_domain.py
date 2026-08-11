from datetime import datetime, timezone as dt_timezone

from django.test import SimpleTestCase

from scuba.chat.domain import (
    Message, MessageType, conversation_partition_key,
    generate_message_id, message_sort_key,
)


class TestMessageTypeAll(SimpleTestCase):
    def test_contains_every_declared_message_type(self):
        self.assertEqual(set(MessageType.ALL), {
            MessageType.TEXT, MessageType.SYSTEM, MessageType.DIVE, MessageType.DIVE_PLAN,
            MessageType.DIVE_SITE, MessageType.LOGBOOK_ENTRY, MessageType.EQUIPMENT,
            MessageType.MARKETPLACE_ITEM,
        })


class TestGenerateMessageId(SimpleTestCase):
    def test_returns_a_32_character_hex_string(self):
        message_id = generate_message_id()
        self.assertEqual(len(message_id), 32)
        int(message_id, 16)  # raises ValueError if it isn't hex

    def test_generates_unique_ids(self):
        self.assertNotEqual(generate_message_id(), generate_message_id())


class TestKeyBuilders(SimpleTestCase):
    def test_conversation_partition_key(self):
        self.assertEqual(conversation_partition_key('abc123'), 'CONVERSATION#abc123')

    def test_message_sort_key_includes_timestamp_and_id(self):
        created_at = datetime(2026, 8, 11, 14, 31, 12, tzinfo=dt_timezone.utc)

        key = message_sort_key(created_at, 'abc123')

        self.assertEqual(key, f"MESSAGE#{created_at.isoformat()}#abc123")

    def test_two_messages_in_the_same_millisecond_get_distinct_sort_keys(self):
        created_at = datetime(2026, 8, 11, 14, 31, 12, 182000, tzinfo=dt_timezone.utc)

        key_one = message_sort_key(created_at, generate_message_id())
        key_two = message_sort_key(created_at, generate_message_id())

        self.assertNotEqual(key_one, key_two)


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

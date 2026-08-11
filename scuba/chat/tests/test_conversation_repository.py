import uuid

from django.test import TestCase
from django.utils import timezone

from scuba.accounts.models import User
from scuba.chat.models import ConversationType
from scuba.chat.repositories.conversation_repository import DjangoConversationRepository


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestDjangoConversationRepository(TestCase):
    def setUp(self):
        self.repo = DjangoConversationRepository()
        self.user_a = _make_user('ca@nowhere.com', 'convusera')
        self.user_b = _make_user('cb@nowhere.com', 'convuserb')

    def test_create_conversation(self):
        conversation = self.repo.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.user_a.id), title='Trip')

        self.assertEqual(conversation.title, 'Trip')
        self.assertEqual(str(conversation.created_by_id), str(self.user_a.id))

    def test_get_conversation_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_conversation(str(uuid.uuid4())))

    def test_get_conversation_returns_a_created_conversation(self):
        created = self.repo.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.user_a.id))

        found = self.repo.get_conversation(str(created.id))

        self.assertEqual(found.id, created.id)

    def test_get_or_create_direct_conversation_adds_both_users_as_participants(self):
        conversation = self.repo.get_or_create_direct_conversation(
            str(self.user_a.id), str(self.user_b.id))

        self.assertEqual(conversation.conversation_type, ConversationType.DIRECT)
        participant_ids = set(conversation.participants.values_list('user_id', flat=True))
        self.assertEqual(participant_ids, {self.user_a.id, self.user_b.id})

    def test_get_or_create_direct_conversation_is_idempotent(self):
        first = self.repo.get_or_create_direct_conversation(str(self.user_a.id), str(self.user_b.id))

        second = self.repo.get_or_create_direct_conversation(str(self.user_a.id), str(self.user_b.id))

        self.assertEqual(first.id, second.id)

    def test_get_or_create_direct_conversation_is_symmetric(self):
        first = self.repo.get_or_create_direct_conversation(str(self.user_a.id), str(self.user_b.id))

        second = self.repo.get_or_create_direct_conversation(str(self.user_b.id), str(self.user_a.id))

        self.assertEqual(first.id, second.id)

    def test_get_or_create_direct_conversation_rejects_the_same_user_twice(self):
        with self.assertRaises(ValueError):
            self.repo.get_or_create_direct_conversation(str(self.user_a.id), str(self.user_a.id))

    def test_update_last_message(self):
        conversation = self.repo.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.user_a.id))
        sent_at = timezone.now()

        self.repo.update_last_message(str(conversation.id), message_id='abc123', sent_at=sent_at)

        conversation.refresh_from_db()
        self.assertEqual(conversation.last_message_id, 'abc123')
        self.assertEqual(conversation.last_message_at, sent_at)

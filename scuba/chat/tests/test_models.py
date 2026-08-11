from django.db import IntegrityError
from django.test import TestCase

from scuba.accounts.models import User
from scuba.chat.models import (
    Conversation, ConversationParticipant, ConversationRole, ConversationType,
    DirectConversationPair,
)


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestConversation(TestCase):
    def setUp(self):
        self.user = _make_user('creator@nowhere.com', 'creatoruser')

    def test_str_uses_title_when_set(self):
        conversation = Conversation.objects.create(
            conversation_type=ConversationType.GROUP, created_by=self.user, title='Dive Buddies')

        self.assertEqual(str(conversation), 'Dive Buddies')

    def test_str_falls_back_to_type_and_id_without_a_title(self):
        conversation = Conversation.objects.create(
            conversation_type=ConversationType.DIRECT, created_by=self.user)

        self.assertIn('Direct conversation', str(conversation))
        self.assertIn(conversation.pk_as_str, str(conversation))


class TestConversationParticipant(TestCase):
    def setUp(self):
        self.user_a = _make_user('a@nowhere.com', 'usera')
        self.conversation = Conversation.objects.create(
            conversation_type=ConversationType.GROUP, created_by=self.user_a)

    def test_role_defaults_to_member(self):
        participant = ConversationParticipant.objects.create(
            conversation=self.conversation, user=self.user_a)

        self.assertEqual(participant.role, ConversationRole.MEMBER)

    def test_a_user_cannot_be_added_to_the_same_conversation_twice(self):
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.user_a)

        with self.assertRaises(IntegrityError):
            ConversationParticipant.objects.create(conversation=self.conversation, user=self.user_a)


class TestDirectConversationPair(TestCase):
    def setUp(self):
        self.user_a = _make_user('pa@nowhere.com', 'pairusera')
        self.user_b = _make_user('pb@nowhere.com', 'pairuserb')

    def _ordered_ids(self):
        return sorted([str(self.user_a.id), str(self.user_b.id)])

    def test_rejects_a_pair_stored_out_of_canonical_order(self):
        conversation = Conversation.objects.create(
            conversation_type=ConversationType.DIRECT, created_by=self.user_a)
        user_low, user_high = self._ordered_ids()

        with self.assertRaises(IntegrityError):
            DirectConversationPair.objects.create(
                conversation=conversation, user_low_id=user_high, user_high_id=user_low)

    def test_rejects_a_duplicate_pair(self):
        user_low, user_high = self._ordered_ids()
        conversation_one = Conversation.objects.create(
            conversation_type=ConversationType.DIRECT, created_by=self.user_a)
        DirectConversationPair.objects.create(
            conversation=conversation_one, user_low_id=user_low, user_high_id=user_high)

        conversation_two = Conversation.objects.create(
            conversation_type=ConversationType.DIRECT, created_by=self.user_a)
        with self.assertRaises(IntegrityError):
            DirectConversationPair.objects.create(
                conversation=conversation_two, user_low_id=user_low, user_high_id=user_high)

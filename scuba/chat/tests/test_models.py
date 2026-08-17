from django.db import IntegrityError, transaction
from django.test import TestCase

from scuba.accounts.models import User
from scuba.chat.models import Conversation, ConversationParticipant


def _make_user(name):
    return User.objects.create_user(
        email=f'{name}@nowhere.com', username=name, password='tester1234',
        first_name=name, last_name='Diver')


class TestConversation(TestCase):
    def setUp(self):
        self.user_a = _make_user('convusera')
        self.user_b = _make_user('convuserb')

    def test_group_conversation_has_no_direct_key(self):
        conversation = Conversation.objects.create(
            conversation_type=Conversation.ConversationType.GROUP,
            created_by=self.user_a,
            title='Wreck Divers',
        )
        self.assertIsNone(conversation.direct_participants_key)

    def test_multiple_group_conversations_do_not_collide(self):
        Conversation.objects.create(
            conversation_type=Conversation.ConversationType.GROUP, created_by=self.user_a)
        Conversation.objects.create(
            conversation_type=Conversation.ConversationType.GROUP, created_by=self.user_a)

        self.assertEqual(Conversation.objects.count(), 2)

    def test_direct_key_for_is_order_independent(self):
        forward = Conversation.direct_key_for(self.user_a.id, self.user_b.id)
        backward = Conversation.direct_key_for(self.user_b.id, self.user_a.id)

        self.assertEqual(forward, backward)

    def test_duplicate_direct_participants_key_is_rejected_at_db_layer(self):
        direct_key = Conversation.direct_key_for(self.user_a.id, self.user_b.id)
        Conversation.objects.create(
            conversation_type=Conversation.ConversationType.DIRECT,
            created_by=self.user_a,
            direct_participants_key=direct_key,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Conversation.objects.create(
                    conversation_type=Conversation.ConversationType.DIRECT,
                    created_by=self.user_b,
                    direct_participants_key=direct_key,
                )


class TestConversationParticipant(TestCase):
    def setUp(self):
        self.user = _make_user('participantuser')
        self.conversation = Conversation.objects.create(
            conversation_type=Conversation.ConversationType.GROUP, created_by=self.user)

    def test_role_defaults_to_member(self):
        participant = ConversationParticipant.objects.create(
            conversation=self.conversation, user=self.user)

        self.assertEqual(participant.role, ConversationParticipant.Role.MEMBER)

    def test_duplicate_participant_is_rejected_at_db_layer(self):
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConversationParticipant.objects.create(
                    conversation=self.conversation, user=self.user)

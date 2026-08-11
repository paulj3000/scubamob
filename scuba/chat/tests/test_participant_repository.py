from django.test import TestCase
from django.utils import timezone

from scuba.accounts.models import User
from scuba.chat.models import Conversation, ConversationParticipant, ConversationRole, ConversationType
from scuba.chat.repositories.participant_repository import DjangoParticipantRepository


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestDjangoParticipantRepository(TestCase):
    def setUp(self):
        self.repo = DjangoParticipantRepository()
        self.user = _make_user('pu@nowhere.com', 'participantuser')
        self.other = _make_user('po@nowhere.com', 'participantother')
        self.conversation = Conversation.objects.create(
            conversation_type=ConversationType.GROUP, created_by=self.user)

    def test_add_participant_defaults_to_member(self):
        participant = self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        self.assertEqual(participant.role, ConversationRole.MEMBER)

    def test_add_participant_is_idempotent(self):
        first = self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        second = self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        self.assertEqual(first.id, second.id)
        self.assertEqual(
            ConversationParticipant.objects.filter(
                conversation=self.conversation, user=self.user).count(),
            1)

    def test_remove_participant(self):
        self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        self.repo.remove_participant(str(self.conversation.id), str(self.user.id))

        self.assertFalse(
            ConversationParticipant.objects.filter(
                conversation=self.conversation, user=self.user).exists())

    def test_list_participants(self):
        self.repo.add_participant(str(self.conversation.id), str(self.user.id))
        self.repo.add_participant(str(self.conversation.id), str(self.other.id))

        participants = self.repo.list_participants(str(self.conversation.id))

        self.assertEqual({p.user_id for p in participants}, {self.user.id, self.other.id})

    def test_is_participant_true_for_a_current_member(self):
        self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        self.assertTrue(self.repo.is_participant(str(self.conversation.id), str(self.user.id)))

    def test_is_participant_false_after_leaving(self):
        self.repo.add_participant(str(self.conversation.id), str(self.user.id))
        ConversationParticipant.objects.filter(
            conversation=self.conversation, user=self.user).update(left_at=timezone.now())

        self.assertFalse(self.repo.is_participant(str(self.conversation.id), str(self.user.id)))

    def test_get_participant_returns_none_when_absent(self):
        self.assertIsNone(self.repo.get_participant(str(self.conversation.id), str(self.user.id)))

    def test_mark_read_updates_last_read_fields(self):
        self.repo.add_participant(str(self.conversation.id), str(self.user.id))

        self.repo.mark_read(str(self.conversation.id), str(self.user.id), last_read_message_id='abc123')

        participant = ConversationParticipant.objects.get(conversation=self.conversation, user=self.user)
        self.assertEqual(participant.last_read_message_id, 'abc123')
        self.assertIsNotNone(participant.last_read_at)

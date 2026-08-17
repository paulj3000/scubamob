from datetime import timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from scuba.accounts.models import User
from scuba.chat.domain import Message, MessageType, generate_message_id
from scuba.chat.exceptions import MessageNotFoundError
from scuba.chat.models import Conversation, ConversationParticipant
from scuba.chat.repositories.attachment_repository import AttachmentRepository
from scuba.chat.repositories.conversation_repository import (
    ConversationRepository, DjangoConversationRepository)
from scuba.chat.repositories.message_repository import InMemoryMessageRepository, MessageRepository
from scuba.chat.repositories.participant_repository import (
    DjangoParticipantRepository, ParticipantRepository)
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


def _make_user(name):
    return User.objects.create_user(
        email=f'{name}@nowhere.com', username=name, password='tester1234',
        first_name=name, last_name='Diver')


class TestDjangoConversationRepository(TestCase):
    """ The real implementation backing Conversation (Phase 1). """

    def setUp(self):
        self.repo = DjangoConversationRepository()
        self.user_a = _make_user('repouser_a')
        self.user_b = _make_user('repouser_b')

    def test_create_conversation(self):
        conversation = self.repo.create_conversation(
            conversation_type=Conversation.ConversationType.GROUP,
            created_by=self.user_a.id, title='Wreck Divers')

        self.assertEqual(conversation.title, 'Wreck Divers')
        self.assertEqual(conversation.created_by_id, self.user_a.id)

    def test_get_conversation_returns_none_when_missing(self):
        self.assertIsNone(self.repo.get_conversation('00000000-0000-0000-0000-000000000000'))

    def test_get_or_create_direct_conversation_creates_both_participants(self):
        conversation = self.repo.get_or_create_direct_conversation(
            self.user_a.id, self.user_b.id)

        self.assertEqual(conversation.conversation_type, Conversation.ConversationType.DIRECT)
        participant_ids = set(
            ConversationParticipant.objects.filter(
                conversation=conversation).values_list('user_id', flat=True))
        self.assertEqual(participant_ids, {self.user_a.id, self.user_b.id})

    def test_get_or_create_direct_conversation_is_idempotent(self):
        first = self.repo.get_or_create_direct_conversation(self.user_a.id, self.user_b.id)
        second = self.repo.get_or_create_direct_conversation(self.user_a.id, self.user_b.id)

        self.assertEqual(first.id, second.id)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_get_or_create_direct_conversation_ignores_argument_order(self):
        first = self.repo.get_or_create_direct_conversation(self.user_a.id, self.user_b.id)
        second = self.repo.get_or_create_direct_conversation(self.user_b.id, self.user_a.id)

        self.assertEqual(first.id, second.id)

    def test_update_last_message(self):
        conversation = self.repo.create_conversation(
            conversation_type=Conversation.ConversationType.DIRECT, created_by=self.user_a.id)
        sent_at = timezone.now()

        self.repo.update_last_message(conversation.id, message_id='msg1', sent_at=sent_at)

        conversation.refresh_from_db()
        self.assertEqual(conversation.last_message_id, 'msg1')
        self.assertEqual(conversation.last_message_at, sent_at)


class TestDjangoParticipantRepository(TestCase):
    """ The real implementation backing ConversationParticipant (Phase 1). """

    def setUp(self):
        self.repo = DjangoParticipantRepository()
        self.user = _make_user('participantrepouser')
        self.other_user = _make_user('otherparticipantrepouser')
        self.conversation = Conversation.objects.create(
            conversation_type=Conversation.ConversationType.GROUP, created_by=self.user)

    def test_add_participant(self):
        participant = self.repo.add_participant(
            self.conversation.id, self.user.id, role=ConversationParticipant.Role.ADMIN)

        self.assertEqual(participant.role, ConversationParticipant.Role.ADMIN)
        self.assertTrue(self.repo.is_participant(self.conversation.id, self.user.id))

    def test_remove_then_re_add_reactivates_the_same_row(self):
        self.repo.add_participant(
            self.conversation.id, self.user.id, role=ConversationParticipant.Role.MEMBER)
        self.repo.remove_participant(self.conversation.id, self.user.id)
        self.assertFalse(self.repo.is_participant(self.conversation.id, self.user.id))

        self.repo.add_participant(
            self.conversation.id, self.user.id, role=ConversationParticipant.Role.MEMBER)

        self.assertTrue(self.repo.is_participant(self.conversation.id, self.user.id))
        self.assertEqual(
            ConversationParticipant.objects.filter(
                conversation=self.conversation, user=self.user).count(),
            1,
        )

    def test_list_participants_excludes_those_who_left(self):
        self.repo.add_participant(
            self.conversation.id, self.user.id, role=ConversationParticipant.Role.MEMBER)
        self.repo.add_participant(
            self.conversation.id, self.other_user.id, role=ConversationParticipant.Role.MEMBER)
        self.repo.remove_participant(self.conversation.id, self.other_user.id)

        participants = self.repo.list_participants(self.conversation.id)

        self.assertEqual([p.user_id for p in participants], [self.user.id])

    def test_is_participant_false_for_non_member(self):
        self.assertFalse(self.repo.is_participant(self.conversation.id, self.user.id))

    def test_mark_read_sets_last_read_fields(self):
        self.repo.add_participant(
            self.conversation.id, self.user.id, role=ConversationParticipant.Role.MEMBER)

        self.repo.mark_read(self.conversation.id, self.user.id, last_read_message_id='msg1')

        participant = self.repo.get_participant(self.conversation.id, self.user.id)
        self.assertEqual(participant.last_read_message_id, 'msg1')
        self.assertIsNotNone(participant.last_read_at)

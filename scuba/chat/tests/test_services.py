"""
Tests for chat.services (Phase 3). Message-repository-dependent calls
inject the Phase 0 InMemoryMessageRepository fake -- these exercise
service-layer business logic (auth, membership, blocks, payload
validation, authorization), not DynamoDB itself (see
test_dynamodb_message_repository.py for that).
"""
from django.test import TestCase
from django.utils import timezone

from scuba.accounts.models import User
from scuba.chat import services
from scuba.chat.exceptions import (
    BlockedUserError, ConversationNotFoundError, InsufficientRoleError,
    InvalidMessagePayloadError, InvalidSenderError, MessageNotFoundError,
    NotAConversationParticipantError, NotMessageOwnerError,
)
from scuba.chat.models import Conversation, ConversationRole, ConversationType
from scuba.chat.repositories.message_repository import InMemoryMessageRepository


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class ChatServicesTestCase(TestCase):
    def setUp(self):
        self.message_repository = InMemoryMessageRepository()
        self.owner = _make_user('owner@nowhere.com', 'owneruser')
        self.member = _make_user('member@nowhere.com', 'memberuser')
        self.outsider = _make_user('outsider@nowhere.com', 'outsideruser')


class TestCreateConversation(ChatServicesTestCase):
    def test_creates_a_group_conversation_and_makes_the_creator_owner(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id), title='Trip')

        self.assertEqual(conversation.title, 'Trip')
        participant = conversation.participants.get(user=self.owner)
        self.assertEqual(participant.role, ConversationRole.OWNER)

    def test_rejects_direct_type(self):
        with self.assertRaises(ValueError):
            services.create_conversation(
                conversation_type=ConversationType.DIRECT, created_by=str(self.owner.id))


class TestCreateDirectConversation(ChatServicesTestCase):
    def test_delegates_to_get_or_create_direct_conversation(self):
        first = services.create_direct_conversation(str(self.owner.id), str(self.member.id))

        second = services.create_direct_conversation(str(self.member.id), str(self.owner.id))

        self.assertEqual(first.id, second.id)


class TestListConversations(ChatServicesTestCase):
    def test_returns_only_conversations_the_user_belongs_to(self):
        theirs = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.member.id))

        found = services.list_conversations(str(self.owner.id))

        self.assertEqual([c.id for c in found], [theirs.id])


class TestGetConversation(ChatServicesTestCase):
    def test_returns_the_conversation_for_a_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        found = services.get_conversation(
            conversation_id=str(conversation.id), user_id=str(self.owner.id))

        self.assertEqual(found.id, conversation.id)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.get_conversation(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id))

    def test_raises_for_a_nonexistent_conversation(self):
        with self.assertRaises(ConversationNotFoundError):
            services.get_conversation(
                conversation_id='00000000-0000-0000-0000-000000000000', user_id=str(self.owner.id))


class TestUpdateConversation(ChatServicesTestCase):
    def test_owner_can_rename_the_conversation(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id), title='Old')

        updated = services.update_conversation(
            conversation_id=str(conversation.id), actor_id=str(self.owner.id), title='New')

        self.assertEqual(updated.title, 'New')

    def test_a_plain_member_cannot_rename_the_conversation(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        with self.assertRaises(InsufficientRoleError):
            services.update_conversation(
                conversation_id=str(conversation.id), actor_id=str(self.member.id), title='New')


class TestListMessages(ChatServicesTestCase):
    def test_returns_messages_for_a_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.send_message(
            conversation_id=str(conversation.id), sender_id=str(self.owner.id),
            body='hi', message_repository=self.message_repository)

        messages, next_cursor = services.list_messages(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            message_repository=self.message_repository)

        self.assertEqual(len(messages), 1)
        self.assertIsNone(next_cursor)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.list_messages(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id),
                message_repository=self.message_repository)


class TestSendMessage(ChatServicesTestCase):
    def setUp(self):
        super().setUp()
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

    def test_sends_a_message_and_updates_conversation_metadata(self):
        message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi there', message_repository=self.message_repository)

        self.assertEqual(message.body, 'hi there')
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.last_message_id, message.message_id)
        self.assertIsNotNone(self.conversation.last_message_at)

    def test_rejects_a_nonexistent_conversation(self):
        with self.assertRaises(ConversationNotFoundError):
            services.send_message(
                conversation_id='00000000-0000-0000-0000-000000000000',
                sender_id=str(self.owner.id), body='hi', message_repository=self.message_repository)

    def test_rejects_a_non_participant_sender(self):
        with self.assertRaises(NotAConversationParticipantError):
            services.send_message(
                conversation_id=str(self.conversation.id), sender_id=str(self.outsider.id),
                body='hi', message_repository=self.message_repository)

    def test_rejects_an_inactive_sender(self):
        self.owner.is_active = False
        self.owner.save()

        with self.assertRaises(InvalidSenderError):
            services.send_message(
                conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
                body='hi', message_repository=self.message_repository)

    def test_rejects_an_empty_body(self):
        with self.assertRaises(InvalidMessagePayloadError):
            services.send_message(
                conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
                body='   ', message_repository=self.message_repository)

    def test_rejects_an_unknown_message_type(self):
        with self.assertRaises(InvalidMessagePayloadError):
            services.send_message(
                conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
                body='hi', message_type='NOT_A_TYPE', message_repository=self.message_repository)

    def test_blocks_a_direct_message_between_blocked_users(self):
        direct = services.create_direct_conversation(str(self.owner.id), str(self.member.id))
        self.owner.block_buddy(self.member)

        with self.assertRaises(BlockedUserError):
            services.send_message(
                conversation_id=str(direct.id), sender_id=str(self.owner.id),
                body='hi', message_repository=self.message_repository)

    def test_does_not_block_group_messages_between_blocked_users(self):
        self.owner.block_buddy(self.member)

        message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.member.id),
            body='hi', message_repository=self.message_repository)

        self.assertEqual(message.sender_id, str(self.member.id))

    def test_is_idempotent_on_client_message_id(self):
        first = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi', client_message_id='retry-1', message_repository=self.message_repository)

        second = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi again', client_message_id='retry-1', message_repository=self.message_repository)

        self.assertEqual(first.message_id, second.message_id)
        self.assertEqual(second.body, 'hi')


class TestEditMessage(ChatServicesTestCase):
    def setUp(self):
        super().setUp()
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))
        self.message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='original', message_repository=self.message_repository)

    def test_author_can_edit_their_own_message(self):
        edited = services.edit_message(
            conversation_id=str(self.conversation.id), message_id=self.message.message_id,
            editor_id=str(self.owner.id), body='edited', message_repository=self.message_repository)

        self.assertEqual(edited.body, 'edited')
        self.assertIsNotNone(edited.edited_at)

    def test_a_different_participant_cannot_edit_the_message(self):
        with self.assertRaises(NotMessageOwnerError):
            services.edit_message(
                conversation_id=str(self.conversation.id), message_id=self.message.message_id,
                editor_id=str(self.member.id), body='edited', message_repository=self.message_repository)

    def test_a_non_participant_cannot_edit(self):
        with self.assertRaises(NotAConversationParticipantError):
            services.edit_message(
                conversation_id=str(self.conversation.id), message_id=self.message.message_id,
                editor_id=str(self.outsider.id), body='edited', message_repository=self.message_repository)

    def test_raises_when_the_message_is_missing(self):
        with self.assertRaises(MessageNotFoundError):
            services.edit_message(
                conversation_id=str(self.conversation.id), message_id='nope',
                editor_id=str(self.owner.id), body='edited', message_repository=self.message_repository)


class TestDeleteMessage(ChatServicesTestCase):
    def setUp(self):
        super().setUp()
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))
        self.message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.member.id),
            body='to delete', message_repository=self.message_repository)

    def test_author_can_delete_their_own_message(self):
        deleted = services.delete_message(
            conversation_id=str(self.conversation.id), message_id=self.message.message_id,
            deleter_id=str(self.member.id), message_repository=self.message_repository)

        self.assertIsNotNone(deleted.deleted_at)

    def test_an_owner_can_delete_someone_elses_message(self):
        deleted = services.delete_message(
            conversation_id=str(self.conversation.id), message_id=self.message.message_id,
            deleter_id=str(self.owner.id), message_repository=self.message_repository)

        self.assertIsNotNone(deleted.deleted_at)

    def test_a_plain_member_cannot_delete_someone_elses_message(self):
        other_member = _make_user('other@nowhere.com', 'othermemberuser')
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(other_member.id),
            actor_id=str(self.owner.id))

        with self.assertRaises(InsufficientRoleError):
            services.delete_message(
                conversation_id=str(self.conversation.id), message_id=self.message.message_id,
                deleter_id=str(other_member.id), message_repository=self.message_repository)


class TestMarkConversationRead(ChatServicesTestCase):
    def test_updates_last_read_state(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        services.mark_conversation_read(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            last_read_message_id='abc123')

        participant = conversation.participants.get(user=self.owner)
        self.assertEqual(participant.last_read_message_id, 'abc123')
        self.assertIsNotNone(participant.last_read_at)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.mark_conversation_read(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id),
                last_read_message_id='abc123')


class TestGetUnreadCount(ChatServicesTestCase):
    def test_counts_conversations_with_a_new_message_since_last_read(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Conversation.objects.filter(pk=conversation.id).update(
            last_message_id='m1', last_message_at=timezone.now())

        self.assertEqual(services.get_unread_count(str(self.owner.id)), 1)
        self.assertEqual(
            services.get_unread_conversation_ids(str(self.owner.id)), {str(conversation.id)})

    def test_excludes_conversations_read_up_to_date(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Conversation.objects.filter(pk=conversation.id).update(
            last_message_id='m1', last_message_at=timezone.now())

        services.mark_conversation_read(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            last_read_message_id='m1')

        self.assertEqual(services.get_unread_count(str(self.owner.id)), 0)

    def test_zero_for_a_user_with_no_conversations(self):
        self.assertEqual(services.get_unread_count(str(self.outsider.id)), 0)


class TestAddParticipant(ChatServicesTestCase):
    def test_owner_can_add_a_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        participant = services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        self.assertEqual(participant.role, ConversationRole.MEMBER)

    def test_a_plain_member_cannot_add_a_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        with self.assertRaises(InsufficientRoleError):
            services.add_participant(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id),
                actor_id=str(self.member.id))

    def test_cannot_add_participants_to_a_direct_conversation(self):
        direct = services.create_direct_conversation(str(self.owner.id), str(self.member.id))

        with self.assertRaises(ValueError):
            services.add_participant(
                conversation_id=str(direct.id), user_id=str(self.outsider.id),
                actor_id=str(self.owner.id))


class TestRemoveParticipant(ChatServicesTestCase):
    def test_owner_can_remove_a_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        services.remove_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        self.assertFalse(conversation.participants.filter(user=self.member).exists())

    def test_a_plain_member_cannot_remove_another_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        with self.assertRaises(InsufficientRoleError):
            services.remove_participant(
                conversation_id=str(conversation.id), user_id=str(self.owner.id),
                actor_id=str(self.member.id))


class TestLeaveConversation(ChatServicesTestCase):
    def test_sets_left_at_without_deleting_the_row(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

        services.leave_conversation(conversation_id=str(conversation.id), user_id=str(self.member.id))

        participant = conversation.participants.get(user=self.member)
        self.assertIsNotNone(participant.left_at)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.leave_conversation(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id))


class TestArchiveAndMuteConversation(ChatServicesTestCase):
    def test_archive_conversation_sets_the_flag(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        services.archive_conversation(conversation_id=str(conversation.id), user_id=str(self.owner.id))

        participant = conversation.participants.get(user=self.owner)
        self.assertTrue(participant.archived)

    def test_archive_conversation_can_unset_the_flag(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.archive_conversation(conversation_id=str(conversation.id), user_id=str(self.owner.id))

        services.archive_conversation(
            conversation_id=str(conversation.id), user_id=str(self.owner.id), archived=False)

        participant = conversation.participants.get(user=self.owner)
        self.assertFalse(participant.archived)

    def test_mute_conversation_sets_the_flag(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        services.mute_conversation(conversation_id=str(conversation.id), user_id=str(self.owner.id))

        participant = conversation.participants.get(user=self.owner)
        self.assertTrue(participant.muted)

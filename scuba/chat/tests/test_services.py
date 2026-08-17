"""
Tests for chat.services (Phase 3). Message-repository-dependent calls
inject the Phase 0 InMemoryMessageRepository fake -- these exercise
service-layer business logic (auth, membership, blocks, payload
validation, authorization), not DynamoDB itself (see
test_dynamodb_message_repository.py for that).
"""
from io import BytesIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from scuba.accounts.models import User
from scuba.chat import services
from scuba.chat.domain import Attachment, AttachmentType, PresenceState, generate_attachment_id
from scuba.chat.exceptions import (
    AttachmentNotFoundError, BlockedUserError, ConversationNotFoundError, InsufficientRoleError,
    InvalidAttachmentError, InvalidMessagePayloadError, InvalidSenderError, MessageNotFoundError,
    NotAConversationParticipantError, NotAuthorizedToViewPresenceError, NotificationNotFoundError,
    NotMessageOwnerError,
)
from scuba.chat.models import (
    Conversation, ConversationParticipant, ConversationRole, ConversationType, Notification,
)
from scuba.chat.repositories.attachment_repository import (
    InMemoryAttachmentRepository, InMemoryAttachmentStorage,
)
from scuba.chat.repositories.message_repository import InMemoryMessageRepository
from scuba.chat.repositories.presence_repository import InMemoryPresenceRepository
from scuba.chat.repositories.typing_repository import InMemoryTypingRepository, typing_key


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


def _make_image_file(name='photo.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


def _make_pdf_file(name='plan.pdf'):
    return SimpleUploadedFile(name, b'%PDF-1.4\n%%EOF', content_type='application/pdf')


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


class TestScheduleNotifications(ChatServicesTestCase):
    """ Phase 10, §29 -- send_message's step 9, hooked via _schedule_notifications. """

    def setUp(self):
        super().setUp()
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))

    def test_notifies_other_participants_but_not_the_sender(self):
        services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi', message_repository=self.message_repository)

        self.assertEqual(Notification.objects.filter(recipient=self.member).count(), 1)
        self.assertFalse(Notification.objects.filter(recipient=self.owner).exists())

    def test_notification_carries_actor_conversation_and_message_id(self):
        message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi', message_repository=self.message_repository)

        notification = Notification.objects.get(recipient=self.member)
        self.assertEqual(notification.actor, self.owner)
        self.assertEqual(notification.conversation, self.conversation)
        self.assertEqual(notification.message_id, message.message_id)

    def test_skips_a_participant_who_disabled_notifications(self):
        ConversationParticipant.objects.filter(
            conversation=self.conversation, user=self.member
        ).update(notifications_enabled=False)

        services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='hi', message_repository=self.message_repository)

        self.assertFalse(Notification.objects.filter(recipient=self.member).exists())


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


class TestStartTyping(ChatServicesTestCase):
    def test_records_typing_state(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        typing_repository = InMemoryTypingRepository()

        services.start_typing(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            typing_repository=typing_repository)

        self.assertIn(
            typing_key(str(conversation.id), str(self.owner.id)), typing_repository._typing)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.start_typing(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id),
                typing_repository=InMemoryTypingRepository())


class TestStopTyping(ChatServicesTestCase):
    def test_clears_typing_state(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        typing_repository = InMemoryTypingRepository()
        services.start_typing(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            typing_repository=typing_repository)

        services.stop_typing(
            conversation_id=str(conversation.id), user_id=str(self.owner.id),
            typing_repository=typing_repository)

        self.assertNotIn(
            typing_key(str(conversation.id), str(self.owner.id)), typing_repository._typing)

    def test_rejects_a_non_participant(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))

        with self.assertRaises(NotAConversationParticipantError):
            services.stop_typing(
                conversation_id=str(conversation.id), user_id=str(self.outsider.id),
                typing_repository=InMemoryTypingRepository())


class TestMarkUserOnlineAndOffline(ChatServicesTestCase):
    def test_online_then_offline(self):
        presence_repository = InMemoryPresenceRepository()

        services.mark_user_online(user_id=str(self.owner.id), presence_repository=presence_repository)
        self.assertEqual(presence_repository.get_state(str(self.owner.id)), PresenceState.ONLINE)

        services.mark_user_offline(user_id=str(self.owner.id), presence_repository=presence_repository)
        self.assertEqual(
            presence_repository.get_state(str(self.owner.id)), PresenceState.RECENTLY_ACTIVE)


class TestGetPresence(ChatServicesTestCase):
    def test_a_user_can_view_their_own_presence(self):
        presence_repository = InMemoryPresenceRepository()
        presence_repository.mark_connected(str(self.owner.id))

        state = services.get_presence(
            user_id=str(self.owner.id), requester_id=str(self.owner.id),
            presence_repository=presence_repository)

        self.assertEqual(state, PresenceState.ONLINE)

    def test_a_conversation_partner_can_view_presence(self):
        services.create_direct_conversation(str(self.owner.id), str(self.member.id))
        presence_repository = InMemoryPresenceRepository()
        presence_repository.mark_connected(str(self.owner.id))

        state = services.get_presence(
            user_id=str(self.owner.id), requester_id=str(self.member.id),
            presence_repository=presence_repository)

        self.assertEqual(state, PresenceState.ONLINE)

    def test_a_non_partner_is_rejected(self):
        presence_repository = InMemoryPresenceRepository()
        presence_repository.mark_connected(str(self.owner.id))

        with self.assertRaises(NotAuthorizedToViewPresenceError):
            services.get_presence(
                user_id=str(self.owner.id), requester_id=str(self.outsider.id),
                presence_repository=presence_repository)


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


class TestListNotifications(ChatServicesTestCase):
    def test_newest_first_and_scoped_to_the_user(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        first = Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')
        second = Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m2')
        Notification.objects.create(
            recipient=self.outsider, conversation=conversation, actor=self.owner, message_id='m3')

        notifications = services.list_notifications(str(self.member.id))

        self.assertEqual([n.id for n in notifications], [second.id, first.id])

    def test_unread_only(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        unread = Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')
        Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m2',
            read_at=timezone.now())

        notifications = services.list_notifications(str(self.member.id), unread_only=True)

        self.assertEqual([n.id for n in notifications], [unread.id])


class TestGetUnreadNotificationCount(ChatServicesTestCase):
    def test_counts_only_unread_notifications_for_the_user(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')
        Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m2',
            read_at=timezone.now())

        self.assertEqual(services.get_unread_notification_count(str(self.member.id)), 1)


class TestMarkNotificationRead(ChatServicesTestCase):
    def test_marks_a_notification_as_read(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        notification = Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')

        result = services.mark_notification_read(
            notification_id=str(notification.id), user_id=str(self.member.id))

        self.assertIsNotNone(result.read_at)

    def test_raises_for_a_notification_belonging_to_someone_else(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        notification = Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')

        with self.assertRaises(NotificationNotFoundError):
            services.mark_notification_read(
                notification_id=str(notification.id), user_id=str(self.outsider.id))

    def test_raises_for_a_nonexistent_notification(self):
        with self.assertRaises(NotificationNotFoundError):
            services.mark_notification_read(
                notification_id='00000000-0000-0000-0000-000000000000', user_id=str(self.member.id))


class TestMarkAllNotificationsRead(ChatServicesTestCase):
    def test_marks_every_unread_notification_for_the_user(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m1')
        Notification.objects.create(
            recipient=self.member, conversation=conversation, actor=self.owner, message_id='m2')

        services.mark_all_notifications_read(str(self.member.id))

        self.assertEqual(services.get_unread_notification_count(str(self.member.id)), 0)


class ChatAttachmentTestCase(ChatServicesTestCase):
    def setUp(self):
        super().setUp()
        self.attachment_repository = InMemoryAttachmentRepository()
        self.attachment_storage = InMemoryAttachmentStorage()
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.member.id),
            actor_id=str(self.owner.id))
        self.message = services.send_message(
            conversation_id=str(self.conversation.id), sender_id=str(self.owner.id),
            body='look at this', message_repository=self.message_repository)

    def _upload(self, uploaded_file, uploader_id=None):
        return services.upload_attachment(
            conversation_id=str(self.conversation.id), message_id=self.message.message_id,
            uploader_id=uploader_id or str(self.owner.id), uploaded_file=uploaded_file,
            message_repository=self.message_repository,
            attachment_repository=self.attachment_repository,
            attachment_storage=self.attachment_storage)


class TestUploadAttachment(ChatAttachmentTestCase):
    def test_uploads_an_image_and_records_metadata(self):
        attachment = self._upload(_make_image_file())

        self.assertEqual(attachment.attachment_type, AttachmentType.IMAGE)
        self.assertEqual(attachment.message_id, self.message.message_id)
        self.assertEqual(attachment.conversation_id, str(self.conversation.id))
        self.assertIn(attachment.s3_key, self.attachment_storage.objects)

    def test_uploads_a_pdf_document(self):
        attachment = self._upload(_make_pdf_file())

        self.assertEqual(attachment.attachment_type, AttachmentType.DOCUMENT)

    def test_rejects_a_non_participant(self):
        with self.assertRaises(NotAConversationParticipantError):
            self._upload(_make_image_file(), uploader_id=str(self.outsider.id))

    def test_rejects_a_missing_message(self):
        with self.assertRaises(MessageNotFoundError):
            services.upload_attachment(
                conversation_id=str(self.conversation.id), message_id='nope',
                uploader_id=str(self.owner.id), uploaded_file=_make_image_file(),
                message_repository=self.message_repository,
                attachment_repository=self.attachment_repository,
                attachment_storage=self.attachment_storage)

    def test_rejects_a_non_author(self):
        with self.assertRaises(NotMessageOwnerError):
            self._upload(_make_image_file(), uploader_id=str(self.member.id))

    def test_rejects_a_missing_file(self):
        with self.assertRaises(InvalidAttachmentError):
            self._upload(None)

    def test_rejects_an_unsupported_content_type(self):
        upload = SimpleUploadedFile('note.txt', b'hello', content_type='text/plain')
        with self.assertRaises(InvalidAttachmentError):
            self._upload(upload)

    def test_rejects_a_file_that_is_too_large(self):
        with mock.patch.object(services, 'MAX_ATTACHMENT_SIZE', 1):
            with self.assertRaises(InvalidAttachmentError):
                self._upload(_make_image_file())

    def test_rejects_undecodable_image_bytes(self):
        upload = SimpleUploadedFile('fake.png', b'not-really-a-png', content_type='image/png')
        with self.assertRaises(InvalidAttachmentError):
            self._upload(upload)

    def test_rejects_undecodable_pdf_bytes(self):
        upload = SimpleUploadedFile('fake.pdf', b'not-really-a-pdf', content_type='application/pdf')
        with self.assertRaises(InvalidAttachmentError):
            self._upload(upload)


class TestListAttachments(ChatAttachmentTestCase):
    def setUp(self):
        super().setUp()
        self._upload(_make_image_file())

    def test_lists_attachments_for_a_participant(self):
        attachments = services.list_attachments(
            conversation_id=str(self.conversation.id), message_id=self.message.message_id,
            user_id=str(self.owner.id), attachment_repository=self.attachment_repository)

        self.assertEqual(len(attachments), 1)

    def test_rejects_a_non_participant(self):
        with self.assertRaises(NotAConversationParticipantError):
            services.list_attachments(
                conversation_id=str(self.conversation.id), message_id=self.message.message_id,
                user_id=str(self.outsider.id), attachment_repository=self.attachment_repository)


class TestGetAttachment(ChatAttachmentTestCase):
    def setUp(self):
        super().setUp()
        self.attachment = self._upload(_make_image_file())

    def test_returns_the_attachment_for_a_participant(self):
        found = services.get_attachment(
            conversation_id=str(self.conversation.id), attachment_id=self.attachment.attachment_id,
            user_id=str(self.owner.id), attachment_repository=self.attachment_repository)

        self.assertEqual(found.attachment_id, self.attachment.attachment_id)

    def test_rejects_a_non_participant(self):
        with self.assertRaises(NotAConversationParticipantError):
            services.get_attachment(
                conversation_id=str(self.conversation.id), attachment_id=self.attachment.attachment_id,
                user_id=str(self.outsider.id), attachment_repository=self.attachment_repository)

    def test_raises_for_a_missing_attachment(self):
        with self.assertRaises(AttachmentNotFoundError):
            services.get_attachment(
                conversation_id=str(self.conversation.id), attachment_id='nope',
                user_id=str(self.owner.id), attachment_repository=self.attachment_repository)


class TestGetAttachmentDownloadUrl(ChatServicesTestCase):
    def test_returns_a_url_from_the_given_storage(self):
        attachment_storage = InMemoryAttachmentStorage()
        attachment = Attachment(
            attachment_id=generate_attachment_id(),
            conversation_id='conv1',
            message_id='msg1',
            attachment_type=AttachmentType.IMAGE,
            s3_key='chat/conv1/msg1/att1.jpg',
            content_type='image/jpeg',
            size=1024,
            created_at=timezone.now(),
        )

        url = services.get_attachment_download_url(attachment, attachment_storage=attachment_storage)

        self.assertIn(attachment.s3_key, url)

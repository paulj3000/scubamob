from django.test import TestCase

from scuba.accounts.models import User
from scuba.chat.models import Conversation, ConversationType
from scuba.chat.repositories.notification_repository import DjangoNotificationRepository


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestDjangoNotificationRepository(TestCase):
    def setUp(self):
        self.repo = DjangoNotificationRepository()
        self.recipient = _make_user('nr@nowhere.com', 'notifrecipient')
        self.actor = _make_user('na@nowhere.com', 'notifactor')
        self.conversation = Conversation.objects.create(
            conversation_type=ConversationType.GROUP, created_by=self.actor)

    def _create(self, message_id='m1'):
        return self.repo.create_notification(
            recipient_id=str(self.recipient.id), conversation_id=str(self.conversation.id),
            actor_id=str(self.actor.id), message_id=message_id)

    def test_create_notification(self):
        notification = self._create()

        self.assertEqual(str(notification.recipient_id), str(self.recipient.id))
        self.assertEqual(str(notification.conversation_id), str(self.conversation.id))
        self.assertEqual(str(notification.actor_id), str(self.actor.id))
        self.assertEqual(notification.message_id, 'm1')
        self.assertIsNone(notification.read_at)

    def test_list_notifications_newest_first(self):
        first = self._create(message_id='m1')
        second = self._create(message_id='m2')

        notifications = self.repo.list_notifications(str(self.recipient.id))

        self.assertEqual([n.id for n in notifications], [second.id, first.id])

    def test_list_notifications_unread_only(self):
        unread = self._create(message_id='m1')
        read = self._create(message_id='m2')
        self.repo.mark_read(str(read.id), str(self.recipient.id))

        notifications = self.repo.list_notifications(str(self.recipient.id), unread_only=True)

        self.assertEqual([n.id for n in notifications], [unread.id])

    def test_list_notifications_respects_limit(self):
        for i in range(3):
            self._create(message_id=f'm{i}')

        notifications = self.repo.list_notifications(str(self.recipient.id), limit=2)

        self.assertEqual(len(notifications), 2)

    def test_list_notifications_scoped_to_recipient(self):
        self._create()
        other_recipient = _make_user('other@nowhere.com', 'notifother')

        self.assertEqual(self.repo.list_notifications(str(other_recipient.id)), [])

    def test_count_unread(self):
        self._create(message_id='m1')
        read = self._create(message_id='m2')
        self.repo.mark_read(str(read.id), str(self.recipient.id))

        self.assertEqual(self.repo.count_unread(str(self.recipient.id)), 1)

    def test_mark_read_sets_read_at(self):
        notification = self._create()

        updated = self.repo.mark_read(str(notification.id), str(self.recipient.id))

        self.assertIsNotNone(updated.read_at)

    def test_mark_read_is_idempotent(self):
        notification = self._create()
        self.repo.mark_read(str(notification.id), str(self.recipient.id))

        updated_again = self.repo.mark_read(str(notification.id), str(self.recipient.id))

        self.assertIsNotNone(updated_again.read_at)

    def test_mark_read_returns_none_for_a_notification_belonging_to_someone_else(self):
        notification = self._create()
        other_recipient = _make_user('mismatch@nowhere.com', 'notifmismatch')

        self.assertIsNone(self.repo.mark_read(str(notification.id), str(other_recipient.id)))

    def test_mark_all_read(self):
        self._create(message_id='m1')
        self._create(message_id='m2')

        self.repo.mark_all_read(str(self.recipient.id))

        self.assertEqual(self.repo.count_unread(str(self.recipient.id)), 0)

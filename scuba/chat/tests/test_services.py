"""
Phase 0 only defines the service layer's boundary (function signatures);
Phase 3 implements the actual logic. This documents that boundary and
should shrink function-by-function as Phase 3 lands.
"""
from django.test import SimpleTestCase

from scuba.chat import services


class TestServiceLayerIsNotYetImplemented(SimpleTestCase):
    def test_create_conversation_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.create_conversation(conversation_type='DIRECT', created_by='user1')

    def test_create_direct_conversation_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.create_direct_conversation('user1', 'user2')

    def test_send_message_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.send_message(conversation_id='conv1', sender_id='user1', body='hi')

    def test_edit_message_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.edit_message(
                conversation_id='conv1', message_id='m1', editor_id='user1', body='hi')

    def test_delete_message_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.delete_message(conversation_id='conv1', message_id='m1', deleter_id='user1')

    def test_mark_conversation_read_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.mark_conversation_read(
                conversation_id='conv1', user_id='user1', last_read_message_id='m1')

    def test_add_participant_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.add_participant(conversation_id='conv1', user_id='user1', actor_id='user2')

    def test_remove_participant_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.remove_participant(conversation_id='conv1', user_id='user1', actor_id='user2')

    def test_leave_conversation_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.leave_conversation(conversation_id='conv1', user_id='user1')

    def test_archive_conversation_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.archive_conversation(conversation_id='conv1', user_id='user1')

    def test_mute_conversation_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            services.mute_conversation(conversation_id='conv1', user_id='user1')

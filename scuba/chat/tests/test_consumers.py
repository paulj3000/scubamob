"""
Tests for the chat WebSocket consumer (docs/chat_dynamo.md Phase 6,
§22-24). Uses channels.testing.WebsocketCommunicator against the
in-memory channel layer conftest.py configures for the whole test
session -- no live Redis (CLAUDE.md forbids tests depending on a live
external service).
"""
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase

from scuba.accounts.models import User
from scuba.chat import services
from scuba.chat.consumers import ChatConsumer
from scuba.chat.models import ConversationType
from scuba.chat.repositories.message_repository import InMemoryMessageRepository


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestChatConsumerConnection(TransactionTestCase):
    async def test_rejects_an_anonymous_connection(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        communicator.scope['user'] = AnonymousUser()

        connected, _ = await communicator.connect()

        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_accepts_an_authenticated_connection(self):
        user = await database_sync_to_async(_make_user)('consumeruser@nowhere.com', 'consumeruser')
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        await communicator.disconnect()


class TestChatEventBroadcast(TransactionTestCase):
    """
    §24's whole point: a message is persisted first (DynamoDB, via the
    in-memory fake here), then broadcast. These tests exercise that full
    pipeline through chat.services.send_message, not the consumer in
    isolation.
    """

    async def test_send_message_broadcasts_to_every_participant(self):
        owner = await database_sync_to_async(_make_user)('bcowner@nowhere.com', 'bcowner')
        member = await database_sync_to_async(_make_user)('bcmember@nowhere.com', 'bcmember')

        conversation = await database_sync_to_async(services.create_conversation)(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))
        await database_sync_to_async(services.add_participant)(
            conversation_id=str(conversation.id), user_id=str(member.id), actor_id=str(owner.id))

        owner_comm = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        owner_comm.scope['user'] = owner
        member_comm = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        member_comm.scope['user'] = member

        self.assertTrue((await owner_comm.connect())[0])
        self.assertTrue((await member_comm.connect())[0])

        message_repository = InMemoryMessageRepository()
        await database_sync_to_async(services.send_message)(
            conversation_id=str(conversation.id), sender_id=str(owner.id),
            body='hello everyone', message_repository=message_repository)

        owner_event = await owner_comm.receive_json_from(timeout=2)
        member_event = await member_comm.receive_json_from(timeout=2)

        self.assertEqual(owner_event['event'], 'message.created')
        self.assertEqual(owner_event['conversation_id'], str(conversation.id))
        self.assertEqual(owner_event['message']['body'], 'hello everyone')
        self.assertEqual(member_event['event'], 'message.created')
        self.assertEqual(member_event['message']['body'], 'hello everyone')

        await owner_comm.disconnect()
        await member_comm.disconnect()

    async def test_a_non_participant_does_not_receive_the_event(self):
        owner = await database_sync_to_async(_make_user)('bcowner2@nowhere.com', 'bcowner2')
        outsider = await database_sync_to_async(_make_user)('bcoutsider2@nowhere.com', 'bcoutsider2')

        conversation = await database_sync_to_async(services.create_conversation)(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))

        outsider_comm = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        outsider_comm.scope['user'] = outsider
        self.assertTrue((await outsider_comm.connect())[0])

        message_repository = InMemoryMessageRepository()
        await database_sync_to_async(services.send_message)(
            conversation_id=str(conversation.id), sender_id=str(owner.id),
            body='private to owner', message_repository=message_repository)

        self.assertTrue(await outsider_comm.receive_nothing(timeout=1))

        await outsider_comm.disconnect()

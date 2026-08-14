"""
Tests for the chat WebSocket consumer (docs/chat_dynamo.md Phase 6,
§22-24). Uses channels.testing.WebsocketCommunicator against the
in-memory channel layer conftest.py configures for the whole test
session -- no live Redis (CLAUDE.md forbids tests depending on a live
external service).
"""
from unittest import mock

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase

from scuba.accounts.models import User
from scuba.chat import services
from scuba.chat.consumers import ChatConsumer
from scuba.chat.models import ConversationType
from scuba.chat.repositories.message_repository import InMemoryMessageRepository
from scuba.chat.repositories.typing_repository import InMemoryTypingRepository


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


class TestChatConsumerTyping(TransactionTestCase):
    """
    Inbound typing.started/typing.stopped (Phase 8, §27). The default
    typing repository is patched to an in-memory fake for the duration of
    each test -- no live Redis (CLAUDE.md forbids tests depending on a
    live external service); RedisTypingRepository itself is covered
    directly in test_typing_repository.py against fakeredis.
    """

    def setUp(self):
        patcher = mock.patch.object(
            services, '_default_typing_repository', return_value=InMemoryTypingRepository())
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_typing_started_is_broadcast_to_other_participants(self):
        owner = await database_sync_to_async(_make_user)('typeowner@nowhere.com', 'typeowner')
        member = await database_sync_to_async(_make_user)('typemember@nowhere.com', 'typemember')
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

        await owner_comm.send_json_to({'type': 'typing.started', 'conversation_id': str(conversation.id)})

        member_event = await member_comm.receive_json_from(timeout=2)
        self.assertEqual(member_event['event'], 'typing.started')
        self.assertEqual(member_event['conversation_id'], str(conversation.id))
        self.assertEqual(member_event['user_id'], str(owner.id))

        await owner_comm.disconnect()
        await member_comm.disconnect()

    async def test_typing_stopped_is_broadcast_to_other_participants(self):
        owner = await database_sync_to_async(_make_user)('typeowner2@nowhere.com', 'typeowner2')
        member = await database_sync_to_async(_make_user)('typemember2@nowhere.com', 'typemember2')
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

        await owner_comm.send_json_to({'type': 'typing.stopped', 'conversation_id': str(conversation.id)})

        member_event = await member_comm.receive_json_from(timeout=2)
        self.assertEqual(member_event['event'], 'typing.stopped')

        await owner_comm.disconnect()
        await member_comm.disconnect()

    async def test_a_non_participant_typing_event_is_silently_ignored(self):
        owner = await database_sync_to_async(_make_user)('typeowner3@nowhere.com', 'typeowner3')
        outsider = await database_sync_to_async(_make_user)('typeoutsider3@nowhere.com', 'typeoutsider3')
        conversation = await database_sync_to_async(services.create_conversation)(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))

        outsider_comm = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        outsider_comm.scope['user'] = outsider
        self.assertTrue((await outsider_comm.connect())[0])

        await outsider_comm.send_json_to(
            {'type': 'typing.started', 'conversation_id': str(conversation.id)})

        # the socket must stay open (no ChatError propagates into a close)
        self.assertTrue(await outsider_comm.receive_nothing(timeout=1))
        await outsider_comm.send_json_to({'type': 'ping'})
        self.assertTrue(await outsider_comm.receive_nothing(timeout=1))

        await outsider_comm.disconnect()

    async def test_an_unrecognized_message_type_is_ignored(self):
        owner = await database_sync_to_async(_make_user)('typeowner4@nowhere.com', 'typeowner4')
        conversation = await database_sync_to_async(services.create_conversation)(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))

        owner_comm = WebsocketCommunicator(ChatConsumer.as_asgi(), '/ws/chat/')
        owner_comm.scope['user'] = owner
        self.assertTrue((await owner_comm.connect())[0])

        await owner_comm.send_json_to({'type': 'not.a.real.event', 'conversation_id': str(conversation.id)})

        self.assertTrue(await owner_comm.receive_nothing(timeout=1))
        await owner_comm.disconnect()

"""
End-to-end HTTP tests for the chat REST API (docs/chat_dynamo.md Phase 4,
§19). Conversation-only endpoints use a plain TestCase; message endpoints
also mock DynamoDB via moto (real query/put calls through the views'
default DynamoDBMessageRepository, no live AWS).
"""
import uuid
from unittest import mock

import boto3
from django.test import TestCase
from django.utils import timezone
from moto import mock_aws
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.chat import services
from scuba.chat.models import Conversation, ConversationType
from scuba.chat.repositories.presence_repository import InMemoryPresenceRepository
from scuba.settings import CHAT_DYNAMODB_REGION, CHAT_DYNAMODB_TABLE


def _make_user(email, username):
    return User.objects.create_user(
        email=email, username=username, password='tester1234', first_name='Test', last_name='User')


class TestConversationListApi(TestCase):
    def setUp(self):
        self.owner = _make_user('owner@nowhere.com', 'apiowner')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_anonymous_access_is_rejected(self):
        response = APIClient().get('/api/chat/conversations/')

        self.assertEqual(response.status_code, 401)

    def test_lists_only_the_users_conversations(self):
        theirs = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        other = _make_user('other@nowhere.com', 'apiother')
        services.create_conversation(conversation_type=ConversationType.GROUP, created_by=str(other.id))

        response = self.client.get('/api/chat/conversations/')

        self.assertEqual(response.status_code, 200)
        ids = [c['id'] for c in response.json()['conversations']]
        self.assertEqual(ids, [str(theirs.id)])

    def test_creates_a_group_conversation(self):
        response = self.client.post(
            '/api/chat/conversations/', {'conversation_type': 'GROUP', 'title': 'Trip'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['conversation']['title'], 'Trip')

    def test_rejects_direct_type(self):
        response = self.client.post(
            '/api/chat/conversations/', {'conversation_type': 'DIRECT'}, format='json')

        self.assertEqual(response.status_code, 400)


class TestConversationDetailApi(TestCase):
    def setUp(self):
        self.owner = _make_user('owner2@nowhere.com', 'apiowner2')
        self.outsider = _make_user('outsider2@nowhere.com', 'apioutsider2')
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id), title='Original')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_get_returns_the_conversation(self):
        response = self.client.get(f'/api/chat/conversations/{self.conversation.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['conversation']['id'], str(self.conversation.id))

    def test_get_rejects_a_non_participant(self):
        client = APIClient()
        client.force_authenticate(user=self.outsider)

        response = client.get(f'/api/chat/conversations/{self.conversation.id}/')

        self.assertEqual(response.status_code, 403)

    def test_get_returns_404_for_a_missing_conversation(self):
        response = self.client.get(f'/api/chat/conversations/{uuid.uuid4()}/')

        self.assertEqual(response.status_code, 404)

    def test_patch_renames_the_conversation(self):
        response = self.client.patch(
            f'/api/chat/conversations/{self.conversation.id}/', {'title': 'Renamed'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['conversation']['title'], 'Renamed')

    def test_patch_rejects_a_non_admin(self):
        services.add_participant(
            conversation_id=str(self.conversation.id), user_id=str(self.outsider.id),
            actor_id=str(self.owner.id))
        client = APIClient()
        client.force_authenticate(user=self.outsider)

        response = client.patch(
            f'/api/chat/conversations/{self.conversation.id}/', {'title': 'Renamed'}, format='json')

        self.assertEqual(response.status_code, 403)


@mock_aws
class TestConversationMessagesApi(TestCase):
    def setUp(self):
        env_patcher = mock.patch.dict(
            'os.environ', {'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing'})
        env_patcher.start()
        self.addCleanup(env_patcher.stop)

        dynamo_client = boto3.client('dynamodb', region_name=CHAT_DYNAMODB_REGION)
        dynamo_client.create_table(
            TableName=CHAT_DYNAMODB_TABLE,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'message_id', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[{
                'IndexName': 'MessageIdIndex',
                'KeySchema': [{'AttributeName': 'message_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
            }],
            BillingMode='PAY_PER_REQUEST',
        )

        self.owner = _make_user('msgowner@nowhere.com', 'apimsgowner')
        self.outsider = _make_user('msgoutsider@nowhere.com', 'apimsgoutsider')
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_post_sends_a_message(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/', {'body': 'hi'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message']['body'], 'hi')

    def test_post_rejects_a_non_participant(self):
        client = APIClient()
        client.force_authenticate(user=self.outsider)

        response = client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/', {'body': 'hi'}, format='json')

        self.assertEqual(response.status_code, 403)

    def test_post_rejects_an_empty_body(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/', {'body': '   '}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_get_lists_sent_messages(self):
        self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/', {'body': 'hi'}, format='json')

        response = self.client.get(f'/api/chat/conversations/{self.conversation.id}/messages/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertIsNone(data['next_cursor'])

    def test_get_rejects_a_non_participant(self):
        client = APIClient()
        client.force_authenticate(user=self.outsider)

        response = client.get(f'/api/chat/conversations/{self.conversation.id}/messages/')

        self.assertEqual(response.status_code, 403)


class TestConversationReadApi(TestCase):
    def setUp(self):
        self.owner = _make_user('readowner@nowhere.com', 'apireadowner')
        self.conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_marks_read_with_an_explicit_message_id(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/read/',
            {'last_read_message_id': 'abc123'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['last_read_message_id'], 'abc123')

    def test_returns_400_when_no_message_id_given_and_conversation_has_no_messages(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/read/', {}, format='json')

        self.assertEqual(response.status_code, 400)


class TestConversationMuteApi(TestCase):
    def test_mutes_the_conversation(self):
        owner = _make_user('muteowner@nowhere.com', 'apimuteowner')
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f'/api/chat/conversations/{conversation.id}/mute/', {'muted': True}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['muted'])


class TestConversationArchiveApi(TestCase):
    def test_archives_the_conversation(self):
        owner = _make_user('archiveowner@nowhere.com', 'apiarchiveowner')
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(owner.id))
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f'/api/chat/conversations/{conversation.id}/archive/', {'archived': True}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['archived'])


class TestUnreadCountApi(TestCase):
    def setUp(self):
        self.owner = _make_user('unreadowner@nowhere.com', 'apiunreadowner')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_anonymous_access_is_rejected(self):
        response = APIClient().get('/api/chat/unread-count/')

        self.assertEqual(response.status_code, 401)

    def test_zero_with_no_conversations(self):
        response = self.client.get('/api/chat/unread-count/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 0)

    def test_counts_a_conversation_with_an_unread_message(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Conversation.objects.filter(pk=conversation.id).update(
            last_message_id='m1', last_message_at=timezone.now())

        response = self.client.get('/api/chat/unread-count/')

        self.assertEqual(response.json()['unread_count'], 1)

    def test_conversation_list_marks_unread_conversations(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Conversation.objects.filter(pk=conversation.id).update(
            last_message_id='m1', last_message_at=timezone.now())

        response = self.client.get('/api/chat/conversations/')

        self.assertTrue(response.json()['conversations'][0]['unread'])

    def test_marking_read_clears_the_unread_count(self):
        conversation = services.create_conversation(
            conversation_type=ConversationType.GROUP, created_by=str(self.owner.id))
        Conversation.objects.filter(pk=conversation.id).update(
            last_message_id='m1', last_message_at=timezone.now())

        self.client.post(
            f'/api/chat/conversations/{conversation.id}/read/',
            {'last_read_message_id': 'm1'}, format='json')
        response = self.client.get('/api/chat/unread-count/')

        self.assertEqual(response.json()['unread_count'], 0)


class TestDirectConversationApi(TestCase):
    def test_creates_a_direct_conversation(self):
        owner = _make_user('directowner@nowhere.com', 'apidirectowner')
        other = _make_user('directother@nowhere.com', 'apidirectother')
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(f'/api/chat/direct/{other.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['conversation']['conversation_type'], 'DIRECT')

    def test_is_idempotent(self):
        owner = _make_user('directowner2@nowhere.com', 'apidirectowner2')
        other = _make_user('directother2@nowhere.com', 'apidirectother2')
        client = APIClient()
        client.force_authenticate(user=owner)

        first = client.post(f'/api/chat/direct/{other.id}/')
        second = client.post(f'/api/chat/direct/{other.id}/')

        self.assertEqual(first.json()['conversation']['id'], second.json()['conversation']['id'])


class TestPresenceApi(TestCase):
    """
    Phase 9, §28. The default presence repository is patched to an
    in-memory fake for the duration of each test -- no live Redis
    (CLAUDE.md forbids tests depending on a live external service).
    """

    def setUp(self):
        self.presence_repository = InMemoryPresenceRepository()
        patcher = mock.patch.object(
            services, '_default_presence_repository', return_value=self.presence_repository)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.owner = _make_user('presenceowner@nowhere.com', 'apipresenceowner')
        self.member = _make_user('presencemember@nowhere.com', 'apipresencemember')
        self.outsider = _make_user('presenceoutsider@nowhere.com', 'apipresenceoutsider')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_anonymous_access_is_rejected(self):
        response = APIClient().get(f'/api/chat/presence/{self.owner.id}/')

        self.assertEqual(response.status_code, 401)

    def test_a_user_can_view_their_own_presence(self):
        self.presence_repository.mark_connected(str(self.owner.id))

        response = self.client.get(f'/api/chat/presence/{self.owner.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state'], 'ONLINE')

    def test_a_conversation_partner_can_view_presence(self):
        services.create_direct_conversation(str(self.owner.id), str(self.member.id))
        self.presence_repository.mark_connected(str(self.member.id))

        response = self.client.get(f'/api/chat/presence/{self.member.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state'], 'ONLINE')

    def test_a_non_partner_is_rejected(self):
        response = self.client.get(f'/api/chat/presence/{self.outsider.id}/')

        self.assertEqual(response.status_code, 403)

    def test_defaults_to_offline_when_never_connected(self):
        services.create_direct_conversation(str(self.owner.id), str(self.member.id))

        response = self.client.get(f'/api/chat/presence/{self.member.id}/')

        self.assertEqual(response.json()['state'], 'OFFLINE')

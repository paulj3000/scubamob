"""
Tests for UserListApi (CODE_REVIEW.md §3 item 12 -- unauthenticated PII
disclosure). Given a list of user ids, it returned full name + profile
photo for each with no auth and no block check at all.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.sitesettings.models import SystemApi


class TestUserListApi(TestCase):
    def setUp(self):
        SystemApi.objects.create(
            key='AWS_CLOUDFRONT_URL', value='https://cdn.test/', is_active=True)
        self.caller = User.objects.create_user(
            email='caller@nowhere.com', username='calleruser', password='tester1234',
            first_name='Caller', last_name='User')
        self.other = User.objects.create_user(
            email='other@nowhere.com', username='otheruser', password='tester1234',
            first_name='Other', last_name='User')
        self.blocker = User.objects.create_user(
            email='blocker@nowhere.com', username='blockeruser', password='tester1234',
            first_name='Blocker', last_name='User')

    def test_anonymous_access_is_rejected(self):
        client = APIClient()

        response = client.get(
            '/api/messenger/users', {'id': [self.other.pk_as_str]}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_authenticated_caller_gets_basic_info_for_requested_users(self):
        client = APIClient()
        client.force_authenticate(user=self.caller)

        response = client.get(
            '/api/messenger/users', {'id': [self.other.pk_as_str]}, format='json')

        self.assertEqual(response.status_code, 200)
        users = response.json()['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['id'], self.other.pk_as_str)
        self.assertEqual(users[0]['full_name'], self.other.get_full_name())

    def test_a_user_who_blocked_the_caller_is_excluded(self):
        self.blocker.block_buddy(self.caller)

        client = APIClient()
        client.force_authenticate(user=self.caller)

        response = client.get(
            '/api/messenger/users',
            {'id': [self.other.pk_as_str, self.blocker.pk_as_str]}, format='json')

        self.assertEqual(response.status_code, 200)
        users = response.json()['users']
        ids = [user['id'] for user in users]
        self.assertIn(self.other.pk_as_str, ids)
        self.assertNotIn(self.blocker.pk_as_str, ids)

    def test_a_user_the_caller_blocked_is_excluded(self):
        self.caller.block_buddy(self.other)

        client = APIClient()
        client.force_authenticate(user=self.caller)

        response = client.get(
            '/api/messenger/users', {'id': [self.other.pk_as_str]}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['users'], [])

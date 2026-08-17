"""
Tests for chat.repositories.presence_repository (docs/chat_dynamo.md §28,
Phase 9). RedisPresenceRepository is tested against fakeredis, not a live
Redis (CLAUDE.md forbids tests depending on a live external service) --
injected via the constructor's client override, same DI pattern
RedisTypingRepository uses.
"""
import fakeredis
from django.test import SimpleTestCase

from scuba.chat.domain import PresenceState
from scuba.chat.repositories.presence_repository import (
    CONNECTION_TTL_SECONDS, RECENTLY_ACTIVE_TTL_SECONDS, InMemoryPresenceRepository,
    RedisPresenceRepository, presence_connections_key, presence_recent_key,
)


class TestPresenceKeys(SimpleTestCase):
    def test_connections_key(self):
        self.assertEqual(presence_connections_key('user1'), 'chat:presence:conns:user1')

    def test_recent_key(self):
        self.assertEqual(presence_recent_key('user1'), 'chat:presence:recent:user1')


class TestInMemoryPresenceRepository(SimpleTestCase):
    def test_offline_when_never_connected(self):
        repo = InMemoryPresenceRepository()

        self.assertEqual(repo.get_state('user1'), PresenceState.OFFLINE)

    def test_online_while_connected(self):
        repo = InMemoryPresenceRepository()

        repo.mark_connected('user1')

        self.assertEqual(repo.get_state('user1'), PresenceState.ONLINE)

    def test_recently_active_after_the_only_connection_closes(self):
        repo = InMemoryPresenceRepository()
        repo.mark_connected('user1')

        repo.mark_disconnected('user1')

        self.assertEqual(repo.get_state('user1'), PresenceState.RECENTLY_ACTIVE)

    def test_stays_online_while_a_second_connection_is_still_open(self):
        repo = InMemoryPresenceRepository()
        repo.mark_connected('user1')
        repo.mark_connected('user1')

        repo.mark_disconnected('user1')

        self.assertEqual(repo.get_state('user1'), PresenceState.ONLINE)

    def test_reconnecting_clears_recently_active(self):
        repo = InMemoryPresenceRepository()
        repo.mark_connected('user1')
        repo.mark_disconnected('user1')

        repo.mark_connected('user1')

        self.assertEqual(repo.get_state('user1'), PresenceState.ONLINE)

    def test_users_are_independent(self):
        repo = InMemoryPresenceRepository()

        repo.mark_connected('user1')

        self.assertEqual(repo.get_state('user2'), PresenceState.OFFLINE)


class TestRedisPresenceRepository(SimpleTestCase):
    def setUp(self):
        self.client = fakeredis.FakeStrictRedis()
        self.repo = RedisPresenceRepository(client=self.client)

    def test_offline_when_never_connected(self):
        self.assertEqual(self.repo.get_state('user1'), PresenceState.OFFLINE)

    def test_online_while_connected(self):
        self.repo.mark_connected('user1')

        self.assertEqual(self.repo.get_state('user1'), PresenceState.ONLINE)
        ttl = self.client.ttl(presence_connections_key('user1'))
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, CONNECTION_TTL_SECONDS)

    def test_recently_active_after_the_only_connection_closes(self):
        self.repo.mark_connected('user1')

        self.repo.mark_disconnected('user1')

        self.assertEqual(self.repo.get_state('user1'), PresenceState.RECENTLY_ACTIVE)
        self.assertFalse(self.client.exists(presence_connections_key('user1')))
        ttl = self.client.ttl(presence_recent_key('user1'))
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, RECENTLY_ACTIVE_TTL_SECONDS)

    def test_stays_online_while_a_second_connection_is_still_open(self):
        self.repo.mark_connected('user1')
        self.repo.mark_connected('user1')

        self.repo.mark_disconnected('user1')

        self.assertEqual(self.repo.get_state('user1'), PresenceState.ONLINE)

    def test_reconnecting_clears_recently_active(self):
        self.repo.mark_connected('user1')
        self.repo.mark_disconnected('user1')

        self.repo.mark_connected('user1')

        self.assertEqual(self.repo.get_state('user1'), PresenceState.ONLINE)
        self.assertFalse(self.client.exists(presence_recent_key('user1')))

    def test_users_are_independent(self):
        self.repo.mark_connected('user1')

        self.assertEqual(self.repo.get_state('user2'), PresenceState.OFFLINE)

    def test_disconnect_without_a_prior_connect_does_not_go_negative(self):
        self.repo.mark_disconnected('user1')

        self.assertEqual(self.repo.get_state('user1'), PresenceState.RECENTLY_ACTIVE)
        self.assertFalse(self.client.exists(presence_connections_key('user1')))

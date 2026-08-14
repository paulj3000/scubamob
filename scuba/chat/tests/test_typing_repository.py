"""
Tests for chat.repositories.typing_repository (docs/chat_dynamo.md §27,
Phase 8). RedisTypingRepository is tested against fakeredis, not a live
Redis (CLAUDE.md forbids tests depending on a live external service) --
injected via the constructor's client override, same DI pattern
MessageRepository's boto3 client uses.
"""
import fakeredis
from django.test import SimpleTestCase

from scuba.chat.repositories.typing_repository import (
    TYPING_TTL_SECONDS, InMemoryTypingRepository, RedisTypingRepository, typing_key,
)


class TestTypingKey(SimpleTestCase):
    def test_matches_the_documented_key_structure(self):
        self.assertEqual(typing_key('conv1', 'user1'), 'chat:typing:conv1:user1')


class TestInMemoryTypingRepository(SimpleTestCase):
    def test_set_typing_then_clear_typing(self):
        repo = InMemoryTypingRepository()

        repo.set_typing('conv1', 'user1')
        self.assertIn(typing_key('conv1', 'user1'), repo._typing)

        repo.clear_typing('conv1', 'user1')
        self.assertNotIn(typing_key('conv1', 'user1'), repo._typing)

    def test_clear_typing_is_a_no_op_when_never_set(self):
        repo = InMemoryTypingRepository()

        repo.clear_typing('conv1', 'user1')  # must not raise

        self.assertEqual(repo._typing, set())


class TestRedisTypingRepository(SimpleTestCase):
    def setUp(self):
        self.client = fakeredis.FakeStrictRedis()
        self.repo = RedisTypingRepository(client=self.client)

    def test_set_typing_writes_a_ttl_expiring_key(self):
        self.repo.set_typing('conv1', 'user1')

        key = typing_key('conv1', 'user1')
        self.assertTrue(self.client.exists(key))
        ttl = self.client.ttl(key)
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, TYPING_TTL_SECONDS)

    def test_clear_typing_removes_the_key(self):
        self.repo.set_typing('conv1', 'user1')

        self.repo.clear_typing('conv1', 'user1')

        self.assertFalse(self.client.exists(typing_key('conv1', 'user1')))

    def test_keys_for_different_users_are_independent(self):
        self.repo.set_typing('conv1', 'user1')
        self.repo.set_typing('conv1', 'user2')

        self.repo.clear_typing('conv1', 'user1')

        self.assertFalse(self.client.exists(typing_key('conv1', 'user1')))
        self.assertTrue(self.client.exists(typing_key('conv1', 'user2')))

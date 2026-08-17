"""
PresenceRepository interface (docs/chat_dynamo.md §4.3, §28, Phase 9), an
in-memory fake for chat.services unit tests, and the real Redis-backed
implementation.

Presence is deliberately ephemeral (§28: "Presence should also be
ephemeral.") -- never written through to DynamoDB or SQL, same treatment
as typing state (§27). Two keys per user track it:

  chat:presence:conns:<user_id>   a connection count, incremented on every
                                   WebSocket connect and decremented on
                                   every disconnect, so a user with several
                                   open tabs only reads OFFLINE once the
                                   last one closes.
  chat:presence:recent:<user_id>  set with a TTL the moment the connection
                                   count reaches zero, so a just-disconnected
                                   user reads RECENTLY_ACTIVE for a window
                                   before falling back to OFFLINE.

No exact last-seen timestamp is ever stored or exposed (§28: "Avoid
exposing exact last-seen timestamps unless ScubaMob explicitly decides to
make that part of the product.") -- only the three coarse states.
"""
from abc import ABC, abstractmethod

import redis

from scuba.chat.domain import PresenceState
from scuba.chat.exceptions import RepositoryUnavailableError
from scuba.chat.infrastructure.redis import get_client

RECENTLY_ACTIVE_TTL_SECONDS = 300
# Failsafe only: refreshed on every connect/disconnect so a healthy
# connection's count key never actually expires. Bounds how long a count
# left non-zero by a disconnect() that never ran (e.g. a server crash)
# can wrongly keep reporting a user ONLINE.
CONNECTION_TTL_SECONDS = 3600


def presence_connections_key(user_id: str) -> str:
    return f"chat:presence:conns:{user_id}"


def presence_recent_key(user_id: str) -> str:
    return f"chat:presence:recent:{user_id}"


class PresenceRepository(ABC):
    @abstractmethod
    def mark_connected(self, user_id: str) -> None:
        """ One more open WebSocket connection for this user. """

    @abstractmethod
    def mark_disconnected(self, user_id: str) -> None:
        """ One fewer open WebSocket connection for this user. """

    @abstractmethod
    def get_state(self, user_id: str) -> str:
        """ One of PresenceState.ONLINE / RECENTLY_ACTIVE / OFFLINE. """


class InMemoryPresenceRepository(PresenceRepository):
    """ Dict-backed fake for chat.services unit tests. No TTL behavior -- RedisPresenceRepository owns that. """

    def __init__(self):
        self._connections: dict[str, int] = {}
        self._recently_active: set[str] = set()

    def mark_connected(self, user_id: str) -> None:
        self._connections[user_id] = self._connections.get(user_id, 0) + 1
        self._recently_active.discard(user_id)

    def mark_disconnected(self, user_id: str) -> None:
        remaining = self._connections.get(user_id, 0) - 1
        if remaining > 0:
            self._connections[user_id] = remaining
        else:
            self._connections.pop(user_id, None)
            self._recently_active.add(user_id)

    def get_state(self, user_id: str) -> str:
        if self._connections.get(user_id, 0) > 0:
            return PresenceState.ONLINE
        if user_id in self._recently_active:
            return PresenceState.RECENTLY_ACTIVE
        return PresenceState.OFFLINE


class RedisPresenceRepository(PresenceRepository):
    """ Real implementation backed by Redis (§28). """

    def __init__(self, client: redis.Redis = None):
        self._client = client or get_client()

    def mark_connected(self, user_id: str) -> None:
        try:
            connections_key = presence_connections_key(user_id)
            with self._client.pipeline() as pipe:
                pipe.incr(connections_key)
                pipe.expire(connections_key, CONNECTION_TTL_SECONDS)
                pipe.delete(presence_recent_key(user_id))
                pipe.execute()
        except redis.RedisError as error:
            raise RepositoryUnavailableError(str(error)) from error

    def mark_disconnected(self, user_id: str) -> None:
        try:
            connections_key = presence_connections_key(user_id)
            remaining = self._client.decr(connections_key)
            if remaining > 0:
                self._client.expire(connections_key, CONNECTION_TTL_SECONDS)
            else:
                with self._client.pipeline() as pipe:
                    pipe.delete(connections_key)
                    pipe.set(presence_recent_key(user_id), '1', ex=RECENTLY_ACTIVE_TTL_SECONDS)
                    pipe.execute()
        except redis.RedisError as error:
            raise RepositoryUnavailableError(str(error)) from error

    def get_state(self, user_id: str) -> str:
        try:
            connections = self._client.get(presence_connections_key(user_id))
            if connections is not None and int(connections) > 0:
                return PresenceState.ONLINE
            if self._client.exists(presence_recent_key(user_id)):
                return PresenceState.RECENTLY_ACTIVE
            return PresenceState.OFFLINE
        except redis.RedisError as error:
            raise RepositoryUnavailableError(str(error)) from error

"""
TypingRepository interface (docs/chat_dynamo.md §4.3, §27, Phase 8), an
in-memory fake for chat.services unit tests, and the real Redis-backed
implementation.

Typing state is deliberately ephemeral (§27: "Never permanently store
typing indicators.") -- a plain TTL'd key per (conversation, user), never
written through to DynamoDB or SQL.
"""
from abc import ABC, abstractmethod

import redis

from scuba.chat.exceptions import RepositoryUnavailableError
from scuba.chat.infrastructure.redis import get_client

TYPING_TTL_SECONDS = 8


def typing_key(conversation_id: str, user_id: str) -> str:
    """ §27's example key structure: chat:typing:<conversation_id>:<user_id>. """
    return f"chat:typing:{conversation_id}:{user_id}"


class TypingRepository(ABC):
    @abstractmethod
    def set_typing(self, conversation_id: str, user_id: str) -> None:
        """ Marks the user as typing; the key expires on its own (§27). """

    @abstractmethod
    def clear_typing(self, conversation_id: str, user_id: str) -> None:
        """ Explicit typing.stopped -- removes the key immediately. """


class InMemoryTypingRepository(TypingRepository):
    """ Set-backed fake for chat.services unit tests. No TTL behavior -- RedisTypingRepository owns that. """

    def __init__(self):
        self._typing: set[str] = set()

    def set_typing(self, conversation_id: str, user_id: str) -> None:
        self._typing.add(typing_key(conversation_id, user_id))

    def clear_typing(self, conversation_id: str, user_id: str) -> None:
        self._typing.discard(typing_key(conversation_id, user_id))


class RedisTypingRepository(TypingRepository):
    """ Real implementation backed by Redis (§27). """

    def __init__(self, client: redis.Redis = None):
        self._client = client or get_client()

    def set_typing(self, conversation_id: str, user_id: str) -> None:
        try:
            self._client.set(typing_key(conversation_id, user_id), '1', ex=TYPING_TTL_SECONDS)
        except redis.RedisError as error:
            raise RepositoryUnavailableError(str(error)) from error

    def clear_typing(self, conversation_id: str, user_id: str) -> None:
        try:
            self._client.delete(typing_key(conversation_id, user_id))
        except redis.RedisError as error:
            raise RepositoryUnavailableError(str(error)) from error

"""
MessageRepository interface (docs/chat_dynamo.md §15) and an in-memory
fake implementation for local development and tests (§58: "Production may
use DynamoDB, but development must remain easy"; Phase 0 task: "Add
DynamoDB local/test strategy"). CLAUDE.md requires tests never depend on
a live external service, so this dict-backed fake -- not real DynamoDB --
is what chat.services tests use until Phase 2 adds the boto3-backed
implementation behind the same interface.
"""
from abc import ABC, abstractmethod
from typing import Optional

from django.utils import timezone

from scuba.chat.domain import Message
from scuba.chat.exceptions import MessageNotFoundError


class MessageRepository(ABC):
    """ All DynamoDB-specific detail must live behind this interface (§15). """

    @abstractmethod
    def create_message(self, message: Message) -> Message:
        """ Persist a new message. Idempotent on message.client_message_id (§18). """

    @abstractmethod
    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        ...

    @abstractmethod
    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        """ Idempotency lookup (§18): a retried send must not create a duplicate. """

    @abstractmethod
    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        """
        Returns (messages, next_cursor), chronologically ordered.

        Cursor-based, never offset-based (§10) -- DynamoDB Query doesn't
        support offsets.
        """

    @abstractmethod
    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        ...

    @abstractmethod
    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        """ Sets deleted_at rather than removing the item (§40). """


class InMemoryMessageRepository(MessageRepository):
    """ Dict-backed fake. No network calls -- safe for unit tests. """

    def __init__(self):
        self._by_conversation: dict[str, dict[str, Message]] = {}
        self._by_client_id: dict[tuple[str, str], str] = {}

    def create_message(self, message: Message) -> Message:
        if message.client_message_id:
            existing = self.get_message_by_client_id(
                message.conversation_id, message.client_message_id)
            if existing is not None:
                return existing

        conversation = self._by_conversation.setdefault(message.conversation_id, {})
        conversation[message.message_id] = message

        if message.client_message_id:
            key = (message.conversation_id, message.client_message_id)
            self._by_client_id[key] = message.message_id

        return message

    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        return self._by_conversation.get(conversation_id, {}).get(message_id)

    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        message_id = self._by_client_id.get((conversation_id, client_message_id))
        if message_id is None:
            return None
        return self.get_message(conversation_id, message_id)

    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        messages = sorted(
            self._by_conversation.get(conversation_id, {}).values(),
            key=lambda message: message.created_at,
        )
        start = int(cursor) if cursor else 0
        page = messages[start:start + limit]
        next_cursor = str(start + limit) if start + limit < len(messages) else None
        return page, next_cursor

    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        message = self.get_message(conversation_id, message_id)
        if message is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")
        message.body = body
        message.edited_at = timezone.now()
        return message

    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        message = self.get_message(conversation_id, message_id)
        if message is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")
        message.deleted_at = timezone.now()
        return message

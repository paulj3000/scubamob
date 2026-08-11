"""
ConversationRepository interface (docs/chat_dynamo.md §4.3, §14).

Conversations are relational (§5), so the real implementation wraps the
Phase 1 SQL models -- not defined until then. This interface exists now so
chat.services (Phase 3) can be written against it.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class ConversationRepository(ABC):
    @abstractmethod
    def create_conversation(
        self, *, conversation_type: str, created_by: str, title: Optional[str] = None
    ) -> Any:
        ...

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Any]:
        ...

    @abstractmethod
    def get_or_create_direct_conversation(self, user_a: str, user_b: str) -> Any:
        """
        Repeated requests between the same pair of users must return the
        same active direct conversation, never a duplicate (§14).
        """

    @abstractmethod
    def update_last_message(self, conversation_id: str, *, message_id: str, sent_at) -> None:
        """
        Projects DynamoDB's authoritative message into the SQL conversation
        row (§17, §28). Best-effort/repairable, not part of the same
        transaction as the DynamoDB write.
        """

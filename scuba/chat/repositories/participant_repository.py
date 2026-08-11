"""
ParticipantRepository interface (docs/chat_dynamo.md §4.3, §13).

Membership and authorization are relational (§5) -- the real implementation
wraps the Phase 1 ConversationParticipant SQL model.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class ParticipantRepository(ABC):
    @abstractmethod
    def add_participant(self, conversation_id: str, user_id: str, *, role: str) -> Any:
        ...

    @abstractmethod
    def remove_participant(self, conversation_id: str, user_id: str) -> None:
        ...

    @abstractmethod
    def list_participants(self, conversation_id: str) -> list[Any]:
        ...

    @abstractmethod
    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        """ Used by chat.services to enforce §16 step 2 (membership check). """

    @abstractmethod
    def get_participant(self, conversation_id: str, user_id: str) -> Optional[Any]:
        ...

    @abstractmethod
    def mark_read(self, conversation_id: str, user_id: str, *, last_read_message_id: str) -> None:
        """ Updates last_read_message_id / last_read_at (§25). """

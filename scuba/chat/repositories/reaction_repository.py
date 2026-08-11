"""
ReactionRepository interface (docs/chat_dynamo.md §4.3, §38).

Reactions live in DynamoDB alongside messages. The real key design is
deferred to Phase 19 per the roadmap ("Choose the exact key design based
on the access patterns required.") -- this interface just fixes the shape
callers (chat.services) code against.
"""
from abc import ABC, abstractmethod


class ReactionRepository(ABC):
    @abstractmethod
    def add_reaction(self, conversation_id: str, message_id: str, user_id: str, emoji: str) -> None:
        ...

    @abstractmethod
    def remove_reaction(self, conversation_id: str, message_id: str, user_id: str, emoji: str) -> None:
        ...

    @abstractmethod
    def list_reactions(self, conversation_id: str, message_id: str) -> list[dict]:
        ...

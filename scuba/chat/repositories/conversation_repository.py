"""
ConversationRepository interface (docs/chat_dynamo.md §4.3, §14) and the
Django-ORM-backed implementation wrapping the Phase 1 SQL models.

Conversations are relational (§5) -- unlike MessageRepository, there is no
separate in-memory fake here: the real implementation already runs against
SQLite in tests with no external service involved, the same way every
other ScubaMob app's ORM code is tested.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db import IntegrityError, transaction

from scuba.chat.models import Conversation, ConversationParticipant


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


class DjangoConversationRepository(ConversationRepository):
    """ Real implementation, backed by Conversation/ConversationParticipant (Phase 1). """

    def create_conversation(
        self, *, conversation_type: str, created_by: str, title: Optional[str] = None
    ):
        return Conversation.objects.create(
            conversation_type=conversation_type,
            created_by_id=created_by,
            title=title or '',
        )

    def get_conversation(self, conversation_id: str):
        return Conversation.objects.filter(pk=conversation_id).first()

    def get_or_create_direct_conversation(self, user_a: str, user_b: str):
        direct_key = Conversation.direct_key_for(user_a, user_b)

        # The UniqueConstraint on direct_participants_key is the source of
        # truth for "no duplicate direct conversations" (§14); this create
        # attempt races against it rather than checking-then-creating, so
        # concurrent callers can't both observe "doesn't exist yet".
        try:
            with transaction.atomic():
                conversation = Conversation.objects.create(
                    conversation_type=Conversation.ConversationType.DIRECT,
                    created_by_id=user_a,
                    direct_participants_key=direct_key,
                )
                ConversationParticipant.objects.bulk_create([
                    ConversationParticipant(conversation=conversation, user_id=user_a),
                    ConversationParticipant(conversation=conversation, user_id=user_b),
                ])
            return conversation
        except IntegrityError:
            return Conversation.objects.get(direct_participants_key=direct_key)

    def update_last_message(self, conversation_id: str, *, message_id: str, sent_at) -> None:
        Conversation.objects.filter(pk=conversation_id).update(
            last_message_id=message_id, last_message_at=sent_at)

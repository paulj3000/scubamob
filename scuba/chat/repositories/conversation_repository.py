"""
ConversationRepository interface (docs/chat_dynamo.md §4.3, §14) and the
Phase 1 Django-ORM-backed implementation.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db import IntegrityError, transaction

from scuba.chat.models import Conversation, ConversationParticipant, ConversationType, DirectConversationPair


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

    @abstractmethod
    def list_conversations_for_user(self, user_id: str) -> list[Any]:
        """ Every conversation the user currently belongs to (Phase 4, §19). """

    @abstractmethod
    def update_conversation(self, conversation_id: str, *, title: str) -> Any:
        ...


class DjangoConversationRepository(ConversationRepository):
    """ Real implementation backed by the Phase 1 SQL models. """

    def create_conversation(
        self, *, conversation_type: str, created_by: str, title: Optional[str] = None
    ) -> Conversation:
        return Conversation.objects.create(
            conversation_type=conversation_type,
            created_by_id=created_by,
            title=title or '',
        )

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return Conversation.objects.filter(pk=conversation_id).first()

    def get_or_create_direct_conversation(self, user_a: str, user_b: str) -> Conversation:
        user_a, user_b = str(user_a), str(user_b)
        if user_a == user_b:
            raise ValueError("a direct conversation requires two different users")

        user_low, user_high = sorted([user_a, user_b])

        pair = self._get_pair(user_low, user_high)
        if pair is not None:
            return pair.conversation

        try:
            with transaction.atomic():
                conversation = Conversation.objects.create(
                    conversation_type=ConversationType.DIRECT, created_by_id=user_a)
                DirectConversationPair.objects.create(
                    conversation=conversation, user_low_id=user_low, user_high_id=user_high)
                ConversationParticipant.objects.create(conversation=conversation, user_id=user_a)
                ConversationParticipant.objects.create(conversation=conversation, user_id=user_b)
            return conversation
        except IntegrityError:
            # Lost a race with a concurrent request creating the same pair
            # (§14) -- the unique constraint is authoritative; use the row
            # that won instead of our now-rolled-back attempt.
            pair = self._get_pair(user_low, user_high)
            if pair is None:
                raise
            return pair.conversation

    def update_last_message(self, conversation_id: str, *, message_id: str, sent_at) -> None:
        Conversation.objects.filter(pk=conversation_id).update(
            last_message_id=message_id, last_message_at=sent_at)

    def list_conversations_for_user(self, user_id: str) -> list[Conversation]:
        return list(
            Conversation.objects.filter(
                participants__user_id=user_id, participants__left_at__isnull=True
            ).distinct()
        )

    def update_conversation(self, conversation_id: str, *, title: str) -> Optional[Conversation]:
        Conversation.objects.filter(pk=conversation_id).update(title=title)
        return self.get_conversation(conversation_id)

    @staticmethod
    def _get_pair(user_low: str, user_high: str) -> Optional[DirectConversationPair]:
        return DirectConversationPair.objects.filter(
            user_low_id=user_low, user_high_id=user_high
        ).select_related('conversation').first()

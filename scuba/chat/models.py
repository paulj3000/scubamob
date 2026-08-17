"""
Relational chat models (docs/chat_dynamo.md §12/§13, Phase 1).

Messages themselves are not stored here -- they live in DynamoDB (§6,
scuba.chat.domain.Message) -- these two models own membership,
authorization, and conversation metadata, the parts of the chat domain
that are genuinely relational (§5).
"""
from django.db import models
from django.db.models import UniqueConstraint

from scuba.accounts.models import User
from scuba.libs.models.uuidmodel import UUIDModel


class Conversation(UUIDModel):
    class ConversationType(models.TextChoices):
        DIRECT = 'DIRECT'
        GROUP = 'GROUP'
        DIVE = 'DIVE'
        TRIP = 'TRIP'
        SHOP = 'SHOP'
        MARKETPLACE = 'MARKETPLACE'
        SYSTEM = 'SYSTEM'

    conversation_type = models.CharField(max_length=20, choices=ConversationType.choices)
    title = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        User, related_name='chat_conversations_created', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Best-effort projection of DynamoDB's authoritative last message
    # (§17, §28) -- kept in sync by ConversationRepository.update_last_message,
    # not written in the same transaction as the DynamoDB write.
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_id = models.CharField(max_length=64, blank=True)

    # Populated only when conversation_type == DIRECT: the two
    # participants' ids, sorted and joined (see direct_key_for below), so
    # a plain UniqueConstraint can enforce "no duplicate direct
    # conversations between the same pair" (§14) at the DB layer. Left
    # NULL for every other conversation_type -- both SQLite and
    # MySQL/InnoDB treat multiple NULLs in a unique index as distinct, so
    # non-direct rows never collide with each other or with themselves.
    # Deliberately *not* a conditional/partial UniqueConstraint: MySQL
    # has no partial-index support, and CLAUDE.md rules out
    # Postgres-only features and requires SQLite/MySQL parity.
    direct_participants_key = models.CharField(max_length=80, null=True, blank=True, editable=False)

    class Meta:
        db_table = 'chat_conversation'
        constraints = [
            UniqueConstraint(
                fields=['direct_participants_key'],
                name='unique_direct_conversation_pair'),
        ]

    @staticmethod
    def direct_key_for(user_a_id, user_b_id) -> str:
        return '|'.join(sorted([str(user_a_id), str(user_b_id)]))


class ConversationParticipant(UUIDModel):
    class Role(models.TextChoices):
        MEMBER = 'MEMBER'
        ADMIN = 'ADMIN'
        OWNER = 'OWNER'

    conversation = models.ForeignKey(
        Conversation, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='chat_participations', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    last_read_message_id = models.CharField(max_length=64, blank=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    muted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_conversation_participant'
        constraints = [
            UniqueConstraint(
                fields=['conversation', 'user'], name='unique_conversation_participant'),
        ]

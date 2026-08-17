"""
Relational chat models (docs/chat_dynamo.md §12-14, Phase 1).

Conversation membership and permissions are relational; messages
themselves are not (they live in DynamoDB, §5) and have no model here.
"""
from django.db import models

from scuba.accounts.models import User
from scuba.libs.models.uuidmodel import UUIDModel


class ConversationType(models.TextChoices):
    DIRECT = 'DIRECT', 'Direct'
    GROUP = 'GROUP', 'Group'
    DIVE = 'DIVE', 'Dive'
    TRIP = 'TRIP', 'Trip'
    SHOP = 'SHOP', 'Shop'
    MARKETPLACE = 'MARKETPLACE', 'Marketplace'
    SYSTEM = 'SYSTEM', 'System'


class ConversationRole(models.TextChoices):
    MEMBER = 'MEMBER', 'Member'
    ADMIN = 'ADMIN', 'Admin'
    OWNER = 'OWNER', 'Owner'


class Conversation(UUIDModel):
    """ §12. Authoritative for who belongs, who can send, who administers. """
    conversation_type = models.CharField(max_length=16, choices=ConversationType.choices)
    title = models.CharField(max_length=255, blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # A repairable projection of the authoritative DynamoDB message (§17,
    # §28) -- not updated in the same transaction as the DynamoDB write,
    # so it can briefly lag or need reconciliation. last_message_id is a
    # DynamoDB message id (scuba.chat.domain.generate_message_id), not a
    # foreign key.
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_id = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'chat_conversation'
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return self.title or f"{self.get_conversation_type_display()} conversation {self.pk_as_str}"


class ConversationParticipant(UUIDModel):
    """ §13. Controls membership and authorization. """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participations')
    role = models.CharField(max_length=16, choices=ConversationRole.choices, default=ConversationRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    last_read_message_id = models.CharField(max_length=64, null=True, blank=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    muted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_conversation_participant'
        constraints = [
            models.UniqueConstraint(fields=['conversation', 'user'], name='unique_conversation_participant'),
        ]

    def __str__(self):
        return f"{self.user} in conversation {self.conversation_id}"


class Notification(UUIDModel):
    """
    §29, Phase 10: an in-app notification for a chat event ("Chris Kelly
    sent you a message"). Only ever created for MESSAGE_CREATED today
    (chat.services._schedule_notifications) -- email/push channels are
    explicitly out of scope for this phase.
    """
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    # A DynamoDB message id (scuba.chat.domain.generate_message_id), not a
    # foreign key -- same non-FK pattern as Conversation.last_message_id.
    message_id = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read_at'], name='chat_notif_recipient_read_idx'),
        ]

    def __str__(self):
        return f"Notification for {self.recipient} in conversation {self.conversation_id}"


class DirectConversationPair(UUIDModel):
    """
    Enforces §14: at most one active DIRECT conversation between any two
    users. user_low/user_high hold the pair's two user ids in a canonical
    order (lexicographically by id), so (a, b) and (b, a) always collide
    on the same row. A plain UniqueConstraint -- not a partial/conditional
    index -- so it behaves identically on SQLite and MySQL.
    """
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='direct_pair')
    user_low = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    user_high = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    class Meta:
        db_table = 'chat_direct_conversation_pair'
        constraints = [
            models.UniqueConstraint(
                fields=['user_low', 'user_high'], name='unique_direct_conversation_pair'),
            models.CheckConstraint(
                condition=models.Q(user_low_id__lt=models.F('user_high_id')),
                name='direct_conversation_pair_canonical_order'),
        ]

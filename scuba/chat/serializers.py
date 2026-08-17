"""
DRF serializers for the chat REST API (docs/chat_dynamo.md Phase 4, §19).
"""
from rest_framework import serializers

from scuba.chat.domain import MessageType
from scuba.chat.models import Conversation, ConversationType, Notification


class ConversationSerializer(serializers.ModelSerializer):
    """
    'unread' (Phase 7, §25) is the requesting user's read state, not a
    model field -- it resolves from the 'unread_conversation_ids' context
    key (see chat.apis._conversation_context) and defaults to False when
    that key is absent.
    """
    unread = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            'id', 'conversation_type', 'title', 'created_by',
            'created_at', 'updated_at', 'last_message_at', 'last_message_id', 'unread',
        )
        read_only_fields = (
            'id', 'conversation_type', 'title', 'created_by',
            'created_at', 'updated_at', 'last_message_at', 'last_message_id',
        )

    def get_unread(self, conversation) -> bool:
        return str(conversation.id) in self.context.get('unread_conversation_ids', set())


class CreateConversationSerializer(serializers.Serializer):
    conversation_type = serializers.ChoiceField(choices=ConversationType.choices)
    title = serializers.CharField(required=False, allow_blank=True, default='')


class UpdateConversationSerializer(serializers.Serializer):
    title = serializers.CharField(allow_blank=True)


class MessageSerializer(serializers.Serializer):
    """ Represents scuba.chat.domain.Message -- not a Django model, so a plain Serializer. """
    message_id = serializers.CharField()
    conversation_id = serializers.CharField()
    sender_id = serializers.CharField()
    message_type = serializers.CharField()
    body = serializers.CharField()
    created_at = serializers.DateTimeField()
    client_message_id = serializers.CharField(allow_null=True)
    edited_at = serializers.DateTimeField(allow_null=True)
    deleted_at = serializers.DateTimeField(allow_null=True)
    reply_to_message_id = serializers.CharField(allow_null=True)
    entity_type = serializers.CharField(allow_null=True)
    entity_id = serializers.CharField(allow_null=True)


class SendMessageSerializer(serializers.Serializer):
    body = serializers.CharField()
    message_type = serializers.ChoiceField(choices=MessageType.ALL, default=MessageType.TEXT)
    client_message_id = serializers.CharField(required=False, allow_null=True, default=None)
    reply_to_message_id = serializers.CharField(required=False, allow_null=True, default=None)
    entity_type = serializers.CharField(required=False, allow_null=True, default=None)
    entity_id = serializers.CharField(required=False, allow_null=True, default=None)


class MarkReadSerializer(serializers.Serializer):
    last_read_message_id = serializers.CharField(required=False, allow_null=True, default=None)


class MuteConversationSerializer(serializers.Serializer):
    muted = serializers.BooleanField(default=True)


class ArchiveConversationSerializer(serializers.Serializer):
    archived = serializers.BooleanField(default=True)


class AttachmentSerializer(serializers.Serializer):
    """
    Represents scuba.chat.domain.Attachment -- not a Django model.
    's3_key' is deliberately not exposed; 'download_url' is a freshly
    signed URL resolved by the view via chat.services.get_attachment_download_url
    and passed in through context (§30), not a model field.
    """
    attachment_id = serializers.CharField()
    conversation_id = serializers.CharField()
    message_id = serializers.CharField()
    attachment_type = serializers.CharField()
    content_type = serializers.CharField()
    size = serializers.IntegerField()
    original_filename = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    download_url = serializers.SerializerMethodField()

    def get_download_url(self, attachment) -> str:
        return self.context.get('download_url')


class NotificationSerializer(serializers.ModelSerializer):
    """ Phase 10, §29: an in-app notification. """

    class Meta:
        model = Notification
        fields = ('id', 'conversation', 'actor', 'message_id', 'created_at', 'read_at')
        read_only_fields = fields

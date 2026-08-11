"""
DRF serializers for the chat REST API (docs/chat_dynamo.md Phase 4, §19).
"""
from rest_framework import serializers

from scuba.chat.domain import MessageType
from scuba.chat.models import Conversation, ConversationType


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = (
            'id', 'conversation_type', 'title', 'created_by',
            'created_at', 'updated_at', 'last_message_at', 'last_message_id',
        )
        read_only_fields = fields


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

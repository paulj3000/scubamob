"""
REST messaging API (docs/chat_dynamo.md Phase 4, §19).

Views only ever call into chat.services -- never a repository directly
(§4.2). The REST API works even without the WebSocket infrastructure
(§19), since real-time delivery is entirely separate (Phase 6).
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from scuba.chat import services
from scuba.chat.exceptions import (
    BlockedUserError, ChatError, ConversationNotFoundError, InsufficientRoleError,
    InvalidMessagePayloadError, InvalidSenderError, MessageNotFoundError,
    NotAConversationParticipantError, NotMessageOwnerError, RepositoryUnavailableError,
)
from scuba.chat.serializers import (
    ArchiveConversationSerializer, ConversationSerializer, CreateConversationSerializer,
    MarkReadSerializer, MessageSerializer, MuteConversationSerializer, SendMessageSerializer,
    UpdateConversationSerializer,
)

_MAX_MESSAGE_PAGE_SIZE = 200

_ERROR_STATUS = {
    ConversationNotFoundError: status.HTTP_404_NOT_FOUND,
    MessageNotFoundError: status.HTTP_404_NOT_FOUND,
    NotAConversationParticipantError: status.HTTP_403_FORBIDDEN,
    InsufficientRoleError: status.HTTP_403_FORBIDDEN,
    NotMessageOwnerError: status.HTTP_403_FORBIDDEN,
    BlockedUserError: status.HTTP_403_FORBIDDEN,
    InvalidSenderError: status.HTTP_400_BAD_REQUEST,
    InvalidMessagePayloadError: status.HTTP_400_BAD_REQUEST,
    RepositoryUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _error_response(error: Exception) -> Response:
    status_code = _ERROR_STATUS.get(type(error), status.HTTP_400_BAD_REQUEST)
    return Response({'error': str(error)}, status=status_code)


class ConversationListApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = services.list_conversations(str(request.user.id))
        return Response({'conversations': ConversationSerializer(conversations, many=True).data})

    def post(self, request):
        serializer = CreateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = services.create_conversation(
                created_by=str(request.user.id), **serializer.validated_data)
        except (ChatError, ValueError) as error:
            return _error_response(error)

        return Response(
            {'conversation': ConversationSerializer(conversation).data},
            status=status.HTTP_201_CREATED)


class ConversationDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = services.get_conversation(
                conversation_id=conversation_id, user_id=str(request.user.id))
        except ChatError as error:
            return _error_response(error)

        return Response({'conversation': ConversationSerializer(conversation).data})

    def patch(self, request, conversation_id):
        serializer = UpdateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = services.update_conversation(
                conversation_id=conversation_id, actor_id=str(request.user.id),
                **serializer.validated_data)
        except ChatError as error:
            return _error_response(error)

        return Response({'conversation': ConversationSerializer(conversation).data})


class ConversationMessagesApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            limit = min(int(request.query_params.get('limit', 50)), _MAX_MESSAGE_PAGE_SIZE)
        except ValueError:
            return Response(
                {'error': 'limit must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        cursor = request.query_params.get('cursor')

        try:
            messages, next_cursor = services.list_messages(
                conversation_id=conversation_id, user_id=str(request.user.id),
                limit=limit, cursor=cursor)
        except ChatError as error:
            return _error_response(error)

        return Response({
            'results': MessageSerializer(messages, many=True).data,
            'next_cursor': next_cursor,
        })

    def post(self, request, conversation_id):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = services.send_message(
                conversation_id=conversation_id, sender_id=str(request.user.id),
                **serializer.validated_data)
        except ChatError as error:
            return _error_response(error)

        return Response({'message': MessageSerializer(message).data}, status=status.HTTP_201_CREATED)


class ConversationReadApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        last_read_message_id = serializer.validated_data.get('last_read_message_id')

        try:
            if last_read_message_id is None:
                conversation = services.get_conversation(
                    conversation_id=conversation_id, user_id=str(request.user.id))
                last_read_message_id = conversation.last_message_id
                if last_read_message_id is None:
                    return Response(
                        {'error': 'conversation has no messages yet'},
                        status=status.HTTP_400_BAD_REQUEST)

            services.mark_conversation_read(
                conversation_id=conversation_id, user_id=str(request.user.id),
                last_read_message_id=last_read_message_id)
        except ChatError as error:
            return _error_response(error)

        return Response({
            'conversation_id': conversation_id, 'last_read_message_id': last_read_message_id,
        })


class ConversationMuteApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        serializer = MuteConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.mute_conversation(
                conversation_id=conversation_id, user_id=str(request.user.id),
                **serializer.validated_data)
        except ChatError as error:
            return _error_response(error)

        return Response({'conversation_id': conversation_id, **serializer.validated_data})


class ConversationArchiveApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        serializer = ArchiveConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.archive_conversation(
                conversation_id=conversation_id, user_id=str(request.user.id),
                **serializer.validated_data)
        except ChatError as error:
            return _error_response(error)

        return Response({'conversation_id': conversation_id, **serializer.validated_data})


class DirectConversationApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            conversation = services.create_direct_conversation(str(request.user.id), user_id)
        except (ChatError, ValueError) as error:
            return _error_response(error)

        return Response({'conversation': ConversationSerializer(conversation).data})

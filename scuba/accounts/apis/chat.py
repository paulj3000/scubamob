import requests

from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.serializers.chat import UserListSerializer, \
    UploadFileSerializer, ChatSerializer

from scuba.settings import CHAT_SERVER


class UserListApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ get

        Return basic display info for a list of user ids, excluding
        anyone the caller has blocked or who has blocked the caller.
        """
        ids = request.query_params.getlist('id')

        try:
            users = [
                user for user in User.objects.filter(id__in=ids)
                if not request.user.is_blocked(user)
            ]
            user_list = UserListSerializer(users, many=True)
            return Response({'users': user_list.data})
        except ValidationError:
            pass

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatWUserApi(APIView):
    """ PollApi

    Get the user's data, something we can use for the api
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get(self, request):
        """ get

        Do the actual get
        """
        user = request.user
        to_query = request.query_params.getlist('uid')

        params = {
            'users': to_query + [user.id],
            'userId': request.user.pk_as_str
        }

        try:
            chat = requests.get(
                f"{CHAT_SERVER}/api/chats/lookup",
                params=params, timeout=5)
            retval = chat.json()

            if retval and retval['chat']:
                # there was a valid chat. Assign "Me" to it
                retval['chat']['me'] = request.user.pk_as_str

            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)

    def post(self, request):
        '''



        uids = request.data.get('uid')
        user = request.user
        if not isinstance(uids, list):
            uids = [uids]

        data = {
            'users': uids + [request.user.pk_as_str],
            'userId': request.user.pk_as_str
        }

        try:
            chat = requests.post(
                f"{SystemApi.get_chat_server()}api/chats/",
                json=data)

            retval = chat.json()
            retval['chat']['me'] = user.pk_as_str
            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)
        '''
        serializer = self.serializer_class(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_201_CREATED)


class UploadFileApi(APIView):
    """ PollApi

    Get the user's data, something we can use for the api
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    parser_classes = [MultiPartParser, FileUploadParser]

    def post(self, request):

        userid = request.user.pk_as_str
        data = [{'userid': userid, 'file': file} for file in request.data.getlist('file')]

        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        retval = {
            'files': [{'file': file['s3file']} for file in serializer.data]
        }

        return Response(retval)


class GetAllChatsApi(APIView):
    """ PollApi

    Get the user's data, something we can use for the api
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ get

        Do the actual get
        """
        user = request.user
        params = {'userId': user.pk_as_str}

        try:
            chat = requests.get(
                f"{CHAT_SERVER}/api/chats/user/all", params=params, timeout=5)
            retval = chat.json()
            retval['me'] = user.pk_as_str
            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)


class GetChatsApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ get

        Do the actual get
        """
        user = request.user
        params = {
            'userId': user.pk_as_str,
            'chatId': request.query_params.get('chatId')
        }

        try:
            chat = requests.get(
                f"{CHAT_SERVER}/api/chats", params=params, timeout=5)
            retval = chat.json()
            retval['me'] = user.pk_as_str
            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)

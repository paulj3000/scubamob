import requests

from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.serializers.chat import UserListSerializer, \
    UploadFileSerializer, ChatSerializer

from scuba.sitesettings.models import SystemApi, ChatApi


class UserListApi(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """ get

        Do the actual get
        """
        user_list = []

        ids = request.query_params.getlist('id')

        try:
            user_list = UserListSerializer(User.objects.filter(id__in=ids), many=True)
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
                f"{SystemApi.get_chat_server()}/api/chats/lookup",
                params=params)
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
        serializer = self.serializer_class(data=request.data)
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

        try:
            retval = ChatApi.get_all_user_chats(user.pk_as_str)
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
            chat = requests.get(f"{SystemApi.get_chat_server()}/api/chats", params=params)
            retval = chat.json()
            retval['me'] = user.pk_as_str
            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)


class GetChatMessagesApi(APIView):
    permission_classes = [IsAuthenticated]
    serializer = ChatSerializer

    def get(self, request):
        """ get

        Do the actual get
        """
        query = request.query_params
        user = request.user
        params = {
            'userId': user.pk_as_str,
            'chatId': query.get('chatId'),
            'limit': 100,
            'page': query.get('page'),
        }

        try:
            chat = requests.get(f"{SystemApi.get_chat_server()}api/messages/last", params=params)
            retval = chat.json()
            retval['me'] = user.pk_as_str
            return Response(retval)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)

    def post(self, request):
        """ get

        Do the actual get
        """
        query = request.query_params
        user = request.user
        user_list = request.data.get('users')

        print(" IN HERE ... ")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_201_CREATED)

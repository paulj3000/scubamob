import requests

from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response

from scuba.sitesettings.models import ChatApi


class GetAllChatsApi(APIView):
    """ GetAllChats

    Get all of the chat users
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """ get

        Do the actual get
        """
        retval = ChatApi.admin_get_all_chats()
        return Response(retval)

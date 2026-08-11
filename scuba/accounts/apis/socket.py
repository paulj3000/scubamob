import os
import requests

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from scuba.settings import ALERTING_SERVER, ALERT_SERVER_ACTIVE, CHAT_SERVER


class SocketApi(generics.GenericAPIView):
    """ PollApi

    Get the user's data, something we can use for the api
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ get

        Do the actual get
        """
        user = request.user

        socket_data = {
            'user': {
                'full_name': user.get_full_name(),
                'id': user.id,
            }
        }

        # socket server stuff
        socket_data['server'] = {'CHAT_SERVER': CHAT_SERVER}
        return Response({'socket': socket_data})


class AlertsApi(generics.GenericAPIView):
    """ PollApi

    Get the user's data, something we can use for the api
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ get

        Do the actual get
        """
        user = request.user

        if not ALERT_SERVER_ACTIVE:
            return Response({'error': 'alert server is offline'}, 400)

        params = {
            'userId': user.id
        }

        if os.environ.get('IS_TEST'):
            return Response({'alerts': []})

        try:
            alerts = requests.get(f"{ALERTING_SERVER}/api/alerts", params=params, timeout=5)
            return Response(alerts.json())
        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)

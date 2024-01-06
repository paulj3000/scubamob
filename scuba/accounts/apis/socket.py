import os
import requests

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from scuba.sitesettings.exceptions import InvalidConfigurationException
from scuba.sitesettings.models import SystemApi


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
        socket = {}
        for setting in SystemApi.get_socket_server_settings():
            socket[setting.key] = setting.value

        socket_data['server'] = socket
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

        params = {
            'userId': user.id
        }

        try:
            url = SystemApi.get_alerting_url()
            if os.environ.get('IS_TEST'):
                return Response({'alerts': []})
            else:
                alerts = requests.get(url, params=params)
                return Response(alerts.json())

        except requests.exceptions.ConnectionError:
            return Response({'error': 'cannot reach chat server'}, 500)
        except InvalidConfigurationException:
            return Response({'error': 'alert server is offline'}, 400)

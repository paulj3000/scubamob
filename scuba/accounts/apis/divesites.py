import requests
import logging

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status

from scuba.accounts.serializers.settings import UserEmailSerializer, UserSettingSerializer
from scuba.accounts.models import UserEmail, User
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException
from scuba.sitesettings.models import SettingsApi


logger = logging.getLogger(__name__)


class UserFavoriteDivesite(generics.ListCreateAPIView):
    """ User Email Serializer

    This handles a new email address being added to
    the system
    """
    serializer_class = UserEmailSerializer

    def get_queryset(self):
        user = self.request.user
        return user.emails.all().order_by('-is_primary',)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'emails': response.data
       })

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'emails': response.data
       })

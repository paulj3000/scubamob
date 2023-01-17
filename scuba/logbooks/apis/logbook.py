import requests
import logging

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from django.http import Http404


from scuba.accounts.serializers.settings import UserEmailSerializer, PrimaryEmailSerializer, UserSettingSerializer
from scuba.accounts.settings import SETTINGS_KEYS
from scuba.accounts.models import UserEmail, User
from scuba.sitesettings.models import LogbookApi
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException, EmailInUseException
from scuba.sitesettings.models import SettingsApi


class GetAllLogbooks(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        user = self.request.user

        logbooks = LogbookApi.get_all_logbooks(user.pk_as_str)
        return Response(logbooks, status=res.status_code)

import requests
import logging

from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from scuba.accounts.serializers.settings import UserEmailSerializer, UserSettingSerializer
from scuba.accounts.models import UserEmail
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException
from scuba.sitesettings.models import SettingsApi


logger = logging.getLogger(__name__)


class UserEmailApi(generics.ListCreateAPIView):
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


class RemoveEmailApi(generics.GenericAPIView):
    def delete(self, request, id, *args, **kwargs):
        user = request.user

        try:
            user.remove_email(id)
            return Response(status=status.HTTP_202_ACCEPTED)
        except InvalidEmailIdException:
            return Response({
                'errors': 'Invalid Email ID'},
                status=status.HTTP_400_BAD_REQUEST)
        except PrimaryEmailIdException:
            return Response({
                'errors': 'Cannot Delete primary Email'},
                status=status.HTTP_400_BAD_REQUEST)


class SetPrimaryEmailObjectApi(generics.GenericAPIView):

    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            user.set_primary_email(request.data.get('id'))
            user_emails = UserEmailSerializer(user.get_emails(), many=True)
            return Response({'emails': user_emails.data})
        except InvalidEmailIdException:
            return Response({'errors': 'Invalid Email ID'}, status=status.HTTP_400_BAD_REQUEST)

        return UserEmail.objects.filter(id=self.kwargs['id'], is_primary=False)


class UserSettingApi(generics.GenericAPIView):
    lookup_field = 'setting'
    serializer_class = UserSettingSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if self.kwargs.get(self.lookup_field):
            settings = self.kwargs[self.lookup_field].replace('-', '_')
            settings = [settings]
        else:
            settings = request.query_params.get('settings').split(',')

        url = SettingsApi.get_user_settings_with_options(user.pk_as_str, settings)

        res = requests.get(url, timeout=5)
        return Response(res.json(), status=res.status_code)

    def post(self, request, *args, **kwargs):
        user = self.request.user

        url = SettingsApi.post_user_settings(user.pk_as_str)

        res = requests.post(url, json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)


class UserGeneralSettingListApi(generics.GenericAPIView):
    serializer_class = UserSettingSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user

        return Response({
            'full_name': user.get_full_name(),
            'email': user.email,
            'username': user.username,
        })


class UserSettingListApi(generics.GenericAPIView):
    lookup_field = 'setting'
    serializer_class = UserSettingSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        settings = request.query_params.get('settings')

        if not settings:
            return Response({'error': 'no settings sent in'}, status=status.HTTP_400_BAD_REQUEST)

        url = SettingsApi.get_user_setting_list(user.pk_as_str, settings.split(','))

        try:
            res = requests.get(url, timeout=5)
            return Response(res.json(), status=res.status_code)
        except requests.exceptions.ConnectionError:
            logger.error(url)

            return Response({'error': 'cannot connect to settings'}, status=500)

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.http import Http404

from scuba.accounts.serializers.settings import UserEmailSerializer, PrimaryEmailSerializer, UserSettingSerializer
from scuba.accounts.settings import SETTINGS_KEYS
from scuba.accounts.models import UserEmail
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException, EmailInUseException


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


class UserSettingApi(generics.RetrieveUpdateAPIView):
    lookup_field = 'setting'
    serializer_class = UserSettingSerializer

    def get_queryset(self):
        print(" FIRE 2 ")
        user = self.request.user
        return user.get_setting(self.kwargs[self.lookup_field])

    def get_object(self):
        print(" FOOO **** ")
        user = self.request.user
        return user.get_setting(self.kwargs[self.lookup_field])

        self.kwargs['setting'] = SETTINGS_KEYS[self.kwargs['setting']]

        from pprint import pprint
        pprint(self.kwargs)
        return super().get_object()
        #user = self.request.user
        #return user.get_setting(self.kwargs[self.lookup_field])

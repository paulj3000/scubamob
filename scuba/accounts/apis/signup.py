from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.db import IntegrityError
import json

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny

from scuba.accounts.models import User
from scuba.accounts.exceptions import InvalidUserIdException
import scuba.accounts.serializers.signup as serializers


class ConfirmationCode(generics.GenericAPIView):
    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user

        if user.verify_confirmation_code(request.data.get('code')):
            return Response({'code': True})

        return Response({'code': False})

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        return Response({'code': user.generate_confirmation_code().code})


class SetPassword(generics.GenericAPIView):
    serializer_class = serializers.SetPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        retval = UserSerializer(user).data
        return Response(retval, status=status.HTTP_200_OK)


class SetUsername(generics.GenericAPIView):
    serializer_class = serializers.SetUsernameSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        retval = UserSerializer(user).data
        return Response(retval, status=status.HTTP_200_OK)

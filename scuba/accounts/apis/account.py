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
from scuba.accounts.serializers.account import RegisterUserSerializer, AuthTokenSerializer, UserSerializer


class RegisterUserApi(generics.CreateAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LoginUserApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = AuthTokenSerializer
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

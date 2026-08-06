import os

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

import scuba.accounts.serializers.signup as serializers
from scuba.accounts.exceptions import InvalidConfirmationCodeException


class ConfirmationCode(APIView):
    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user

        try:
            user.verify_confirmation_code(request.data.get('code'))
            user.confirm_user()
            return Response(status=status.HTTP_200_OK)
        except InvalidConfirmationCodeException:
            pass

        return Response({
            'code': 'You supplied an invalid confirmation code'},
            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user

        code = user.generate_confirmation_code().code
        if not os.environ.get('NO_MAIL'):
            user.send_confirmation_code_email(code)
        return Response()


class SetPasswordApi(generics.GenericAPIView):
    serializer_class = serializers.SetPasswordSerializer

    def put(self, request):
        """ put

        Change the logged-in user's password.
        """
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()


class SetUsernameApi(generics.GenericAPIView):
    serializer_class = serializers.SetUsernameSerializer

    def put(self, request):
        """ put

        Change the logged-in user's username.
        """
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUserApi(generics.CreateAPIView):
    serializer_class = serializers.CreateUserSerializer
    permission_classes = (AllowAny,)

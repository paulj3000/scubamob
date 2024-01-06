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
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user})

        if serializer.is_valid():
            return Response()

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SetUsernameApi(generics.GenericAPIView):
    serializer_class = serializers.SetUsernameSerializer
    permission_classes = (AllowAny,)

    def put(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user})

        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUserApi(generics.CreateAPIView):
    serializer_class = serializers.CreateUserSerializer
    permission_classes = (AllowAny,)

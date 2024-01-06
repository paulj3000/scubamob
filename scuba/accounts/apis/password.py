import logging

from django.contrib.auth.forms import PasswordResetForm
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics

from scuba.accounts.serializers.password import PasswordResetSerializer


logger = logging.getLogger(__name__)


class PasswordResetApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        form = PasswordResetForm(request.data)

        # send this off to our logger
        logging.info(f"Password reset for: {request.data['email']}")

        if form.is_valid():
            form.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

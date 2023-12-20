from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny

from scuba.accounts.models import User

from django.core.exceptions import ValidationError


# TODO: Find a proper location for this
class ValidateUserId(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, id, *args, **kwargs):
        retval = None
        status = 200
        try:
            User.objects.get(id=id)
            retval = True
        except (User.DoesNotExist, ValidationError):
            retval = False
            status = 400

        return Response({'user': {'is_valid': retval}}, status=status)

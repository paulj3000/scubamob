from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

import json

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from scuba.accounts.models import User
from scuba.accounts.exceptions import InvalidUserIdException
from scuba.accounts.models import UserBlocked
from scuba.accounts.serializers.profile import ProfileSerializer, \
    BlockUserSerializer, AddBuddySerializer, \
    CancelBuddyRequestSerializer, ConfirmBuddyRequestSerializer

from scuba.accounts.serializers.buddies import BuddySerializer


class GetProfileApi(generics.RetrieveAPIView):
    lookup_field = 'email'
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)

        kwargs = {}
        kwargs[self.lookup_field] = id
        return User.objects.filter(**kwargs)


class GetMeProfileApi(generics.GenericAPIView):
    lookup_field = 'username'
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        user = self.serializer_class(request.user)
        return Response({'profile': user.data})

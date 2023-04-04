from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.db import IntegrityError
import json

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from scuba.accounts.models import User
from scuba.accounts.exceptions import InvalidUserIdException
from scuba.accounts.serializers.buddies import BlockUserSerializer, \
    AddBuddySerializer, AcceptBuddyRequestSerializer, BuddySerializer, \
    RemoveBuddySerializer


class GetBuddiesListApi(generics.ListAPIView):
    """ Get Buddies List

    Return all of the buddies for this particular user
    """
    serializer_class = BuddySerializer

    def get_queryset(self):
        user = self.request.user
        return user.get_all_buddies()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'buddies': response.data
       })


class BlockUserApi(generics.CreateAPIView):
    """ Block User

    Block a particular user
    """
    serializer_class = BlockUserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)


class BuddyStatusApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = BlockUserSerializer

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        buddyid = request.query_params.get('userid')

        if buddyid:
            try:
                return Response(user.get_buddy_status(buddyid))
            except InvalidUserIdException:
                return Response({'errors': 'bad buddy id'},
                        status=status.HTTP_400_BAD_REQUEST)
        # return the response of the password generation
        return Response({'errors': 'missing params'},
                status=status.HTTP_400_BAD_REQUEST)


class AddBuddyApi(generics.CreateAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = AddBuddySerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({'message': 'Buddy Request Sent'},
            status=status.HTTP_201_CREATED)


class BuddyRequestListApi(generics.ListAPIView):
    """ Buddy Request List

    Get a list of buddies the user has requested
    """
    serializer_class = BuddySerializer

    def get_queryset(self):
        user = self.request.user
        return user.get_all_buddy_requests()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'requests': response.data
       })


class BuddyRequestApi(generics.RetrieveDestroyAPIView):
    """ Block User

    Cancel a buddy request
    """
    serializer_class = BuddySerializer


class AcceptBuddyRequestApi(generics.CreateAPIView):
    """ Accept Buddy Request

    Accept a buddy request
    """
    serializer_class = AcceptBuddyRequestSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({
            'accept': serializer.data
        }, status=status.HTTP_201_CREATED)


class RemoveBuddyApi(generics.CreateAPIView):
    """ Remove Buddy Request

    Sadly remove a buddy request
    """
    serializer_class = RemoveBuddySerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)

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
    AddBuddySerializer, AcceptBuddyRequestSerializer, BuddySerializer


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


@login_required
@require_http_methods(["POST"])
def invited(us_request):

    user = us_request.user
    email_invites = []
    response = {'invalid': [], 'sent': [], 'resent': [], 'friends': []}

    if us_request.is_ajax():
        email_data = json.loads(us_request.body)

        friend = None
        from django.core.validators import validate_email

        for email in email_data['email'].split(','):
            # let's get the email and check if it's already in the system
            try:
                # make sure the email address is correct
                validate_email(email)
            except:
                response['invalid'].append(email)
                continue

            # let's see if the user is being a jackass and is inviting himself
            if user.email == email:
                response['invalid'].append(email)
                continue

            friend = None
            try:
                friend = User.objects.get(email=email)
            except:
                pass

            # ok, so far a valid email address.  now, let's check for a valid user
            # first, is this this a valid usre with

            if Friendship.objects.filter(
                Q(friend1__email=email) |
                Q(friend2__email=email)):
                # the user is already a friend.  forget it
                response['friends'].append(email)
                continue

            if UserFriendRequest.objects.filter(friend=user, email=email):
                # the user has already been requested
                response['resent'].append(email)
                continue

            # if we got down here, we can add the new user
            UserFriendRequest.objects.create(friend=user, email=email, user=friend, active=True)
            response['sent'].append(email)

        response['resp'] = 'ok'
        return JSONResponse( response )


@login_required
@require_http_methods(["PUT"])
def accept_invite(us_request):
    response = {}

    user = us_request.user
    return JSONResponse( response )


@login_required
@require_http_methods(["DELETE"])
def delete_friendship(us_request):
    response = {}

    user = us_request.user
    return JSONResponse( response )

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
from scuba.accounts.models import UserBlocked
from scuba.accounts.serializers.buddies import BlockUserSerializer, \
    AddBuddySerializer, CancelBuddyRequestSerializer, \
    ConfirmBuddyRequestSerializer, BuddySerializer


class GetBuddiesListApi(generics.ListAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
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


class BlockUserApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = BlockUserSerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        to_block = self.serializer_class(data=request.data, context={'user': request.user})
        if to_block.is_valid():
            to_block.save()
            return Response({'msg': 'user blocked'}, status=status.HTTP_202_ACCEPTED)

        # return the response of the password generation
        return Response({'errors': to_block.errors}, status=status.HTTP_400_BAD_REQUEST)


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


    def xpost(self, request):
        to_add = self.serializer_class(data=request.data, context={'user': request.user})
        if to_add.is_valid():
            to_add.save()
            return Response({'msg': 'request sent'}, status=status.HTTP_202_ACCEPTED)

        # return the response of the password generation
        return Response({'errors': to_add.errors}, status=status.HTTP_400_BAD_REQUEST)


class CancelBuddyRequestApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = CancelBuddyRequestSerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        to_cancel = self.serializer_class(data=request.data, context={'user': request.user})
        if to_cancel.is_valid():
            to_cancel.save()
            return Response({'msg': 'user blocked'}, status=status.HTTP_202_ACCEPTED)

        # return the response of the password generation
        return Response({'errors': to_block.errors}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmBuddyRequestApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = ConfirmBuddyRequestSerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        to_cancel = self.serializer_class(data=request.data, context={'user': request.user})
        if to_cancel.is_valid():
            to_cancel.save()
            return Response({'msg': 'user blocked'}, status=status.HTTP_202_ACCEPTED)

        # return the response of the password generation
        return Response({'errors': to_cancel.errors}, status=status.HTTP_400_BAD_REQUEST)


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


class GetBuddyStatusApi(generics.GenericAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    def get(self, request):
        from pprint import pprint
        userid = request.query_params.get('userid')

        try:
            buddy_status = request.user.get_buddy_status(userid)
            return Response({'status': buddy_status}, status=status.HTTP_200_OK)
        except InvalidUserIdException:
            error = f"'{userid}' is an invalid user id"
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)


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


@login_required
@require_http_methods(["PUT"])
def add_friend(us_request):
    response = {}
    user = us_request.user

    if us_request.is_ajax():
        request_data = json.loads(us_request.body)
        fid = request_data['fid']
        friend = None

        try:
            friend = User.objects.get(account__guid=fid)
        except:
            pass


        # now, let's try to create a user friend request for this particular user
        try:
            # this may seem backwards, but it is correct.  We want the the user object
            # (at the end) to collect all of his friendships
            UserFriendRequest.objects.create(user=friend, friend=user)
        except IntegrityError:
            response['error'] = True

    return JSONResponse( response )

@login_required
@require_http_methods(["DELETE"])
def cancel_request(us_request):
    response = {}
    user = us_request.user

    if us_request.is_ajax():
        request_data = json.loads(us_request.body)
        fid = request_data['fid']
        friend = None

        try:
            UserFriendRequest.objects.get(friend=user, user__account__guid=fid).delete()
        except:
            raise

    return JSONResponse( response )


@login_required
@require_http_methods(["PUT"])
def accept_request(us_request):
    response = {}
    user = us_request.user

    if us_request.is_ajax():
        request_data = json.loads(us_request.body)
        fid = request_data['fid']
        mode = request_data['mode']

        friend = None
        try:
            friend = User.objects.get(account__guid=fid)
        except:
            pass

        # now, let's try to get the friend request object
        if mode == 'unblock':
            UserFriendBlocked.objects.filter(user=user, friend=friend).delete()
        else:
            try:
                request_obj = UserFriendRequest.objects.get(user=user, friend=friend)
                if mode == 'add':
                    Friendship.objects.create(friend1=user, friend2=friend).save()

                # delete the request object
                request_obj.delete()

            except IntegrityError:
                response['error'] = True

    return JSONResponse( response )

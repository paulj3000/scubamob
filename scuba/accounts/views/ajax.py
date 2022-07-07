import uuid
from pprint import pprint
from datetime import datetime
#import dateutil.parser

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import IntegrityError
import json

#from utils.dateutils import timezone_to_utc, timezone_from_utc
from account.models import Friendship, UserFriendRequest, UserFriendBlocked

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def invited(us_request):

    user    = us_request.user
    email_invites   = []
    response    = { 'invalid': [], 'sent': [], 'resent': [], 'friends': [] }

    if us_request.is_ajax():
        email_data  = json.loads(us_request.body)

        friend    = None
        from django.core.validators import validate_email

        for email in email_data['email'].split(','):
            ## let's get the email and check if it's already in the system
            try:
                ## make sure the email address is correct
                validate_email(email)
            except:
                print "bad email:  %s " % email
                response['invalid'].append(email)
                continue

            ### let's see if the user is being a jackass and is inviting himself
            if user.email == email:
                print "user is inviting himself"
                response['invalid'].append(email)
                continue

            friend  = None
            try:
                friend  = User.objects.get(email=email)
            except:
                pass

            ### ok, so far a valid email address.  now, let's check for a valid user
            ### first, is this this a valid usre with

            if Friendship.objects.filter(
                Q(friend1__email=email) |
                Q(friend2__email=email)):
                ### the user is already a friend.  forget it
                response['friends'].append(email)
                continue

            if UserFriendRequest.objects.filter(friend=user, email=email):
                ### the user has already been requested
                response['resent'].append(email)
                continue

            ## if we got down here, we can add the new user
            UserFriendRequest.objects.create(friend=user, email=email, user=friend, active=True)
            response['sent'].append(email)

        response['resp']    = 'ok'
        return JSONResponse( response )

@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def accept_invite(us_request):
    response    = {}

    user    = us_request.user
    return JSONResponse( response )

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_friendship(us_request):
    response    = {}

    user    = us_request.user
    return JSONResponse( response )


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def add_friend(us_request):
    response    = {}
    user    = us_request.user

    if us_request.is_ajax():
        request_data  = json.loads(us_request.body)
        fid = request_data['fid']
        friend    = None

        try:
            friend = User.objects.get(account__guid=fid)
        except:
            pass


        ### now, let's try to create a user friend request for this particular user
        try:
            ### this may seem backwards, but it is correct.  We want the the user object
            ### (at the end) to collect all of his friendships
            UserFriendRequest.objects.create(user=friend, friend=user)
        except IntegrityError:
            response['error']   = True

    return JSONResponse( response )

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def cancel_request(us_request):
    response    = {}
    user    = us_request.user

    if us_request.is_ajax():
        request_data  = json.loads(us_request.body)
        fid = request_data['fid']
        friend    = None

        try:
            UserFriendRequest.objects.get(friend=user, user__account__guid=fid).delete()
        except:
            raise

    return JSONResponse( response )

@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def block_friend(us_request):
    response    = {}
    user    = us_request.user

    if us_request.is_ajax():
        request_data  = json.loads(us_request.body)
        fid = request_data['fid']

        friend      = User.objects.get(account__guid=fid)
        user.block_friend(friend)

    return JSONResponse( response )

@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def accept_request(us_request):
    response    = {}
    user    = us_request.user

    if us_request.is_ajax():
        request_data  = json.loads(us_request.body)
        fid     = request_data['fid']
        mode    = request_data['mode']

        friend    = None
        try:
            friend = User.objects.get(account__guid=fid)
        except:
            pass

        ### now, let's try to get the friend request object
        if mode == 'unblock':
            UserFriendBlocked.objects.filter(user=user, friend=friend).delete()
        else:
            try:
                request_obj = UserFriendRequest.objects.get(user=user, friend=friend)
                if mode == 'add':
                    Friendship.objects.create(friend1=user, friend2=friend).save()

                #### delete the request object
                request_obj.delete()

            except IntegrityError:
                response['error']   = True

    return JSONResponse( response )


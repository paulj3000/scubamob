# Create your views here.
from pprint import pprint

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
#from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse

from scuba.accounts.forms import EmailInviteForm
from scuba.accounts.models import UserBuddyRequest, UserBuddy


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
                print("bad email:  {email}")
                response['invalid'].append(email)
                continue

            # let's see if the user is being a jackass and is inviting himself
            if user.email == email:
                print("user is inviting himself")
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
                Q(friend1__email=email) | Q(friend2__email=email)):
                # the user is already a friend.  forget it
                response['friends'].append(email)
                continue

            if UserBuddyRequest.objects.filter(friend=user, email=email):
                # the user has already been requested
                response['resent'].append(email)


@login_required
def invite(us_request):
    context = {'title': 'Invite a  Friend'}

    if us_request.method == 'POST':
        email_invite_form = EmailInviteForm(us_request.POST)
        email_invite_form.user = us_request.user
        if email_invite_form.is_valid():
            email_invite_form.save()

            email_invites = email_invite_form.get_email_invites()
    else:
        email_invite_form = EmailInviteForm()

    context.update(us_request, email_invite_form=email_invite_form)
    return render(us_request, "account/friends/invite.html", context)


@login_required
@require_http_methods(["POST", "DELETE"])
def accept(us_request):
    fid = us_request.POST.get('fid')
    delete = us_request.POST.get('delete', False)
    user = us_request.user

    retval = {'data': {}}
    httpclass = HttpResponse

    try:
        UserBuddyRequest.objects.filter(friend=user, user__id=fid).delete()

        if not delete:
            friend = User.objects.get(id=fid)
            UserBuddy.objects.create(user=user, friend=friend)

        retval['data']['items'] = [{'response': 'ok'}]
    except:
        retval['data']['errors'] = [{'response': 'error'}]
        httpclass = HttpResponseBadRequest

    # all is good, let's return this instance
    return JsonResponse(api_response(**retval), httpclass=httpclass)


@login_required
@require_http_methods(["PUT"])
def accept_invite(us_request):
    response = {}

    user = us_request.user
    return JsonResponse(response)


@login_required
@require_http_methods(["DELETE"])
def delete_friendship(us_request):
    response = {}

    user = us_request.user
    return JsonResponse(response)


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
            UserBuddyRequest.objects.create(user=friend, friend=user)
        except IntegrityError:
            response['error'] = True

    return JsonResponse(response)


@login_required
@require_http_methods(["DELETE"])
def delete_friendship(us_request):
    response = {}

    user = us_request.user
    return JsonResponse(response)


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
            UserBuddyRequest.objects.create(user=friend, friend=user)
        except IntegrityError:
            response['error'] = True

    return JsonResponse(response)


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
            UserBuddyRequest.objects.get(friend=user, user__account__guid=fid).delete()
        except:
            raise

    return JsonResponse(response)


@login_required
@require_http_methods(["PUT"])
def block_friend(us_request):
    response = {}
    user = us_request.user

    if us_request.is_ajax():
        request_data = json.loads(us_request.body)
        fid = request_data['fid']

        friend = User.objects.get(account__guid=fid)
        user.block_friend(friend)

    return JsonResponse(response)


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
                request_obj = UserBuddyRequest.objects.get(user=user, friend=friend)
                if mode == 'add':
                    Friendship.objects.create(friend1=user, friend2=friend).save()

                # delete the request object
                request_obj.delete()

            except IntegrityError:
                response['error'] = True

    return JsonResponse(response)

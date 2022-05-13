# Create your views here.
from pprint import pprint

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse

# define the user data for this account
from scuba.accounts.forms import EmailInviteForm
from scuba.accounts.models import UserFriendRequest, UserFriend

from utils.core.user import User


@login_required
def index(us_request, mode=None):
    context = { 'page_title': 'Manage Friends' }
    user = us_request.user

    print(user.get_account())

    UserFriendRequest.objects.update_friend_request_active(user)
    friend_list = us_request.user.friend_user.order_by('friend__first_name')
    friend_request_list = us_request.user.friend_requests.order_by('friend__first_name')

    context.update(csrf(us_request))
    context.update(friend_list=friend_list, friend_request_list=friend_request_list)
    return render(us_request, "friends/index.html", context)

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
                print(f"bad email:  {email}")
                response['invalid'].append(email)
                continue

            ### let's see if the user is being a jackass and is inviting himself
            if user.email == email:
                print("user is inviting himself")
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

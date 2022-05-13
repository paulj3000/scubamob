# Create your views here.
from pprint import pprint

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
#from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse

# define the user data for this account
from account.forms import EmailInviteForm
from account.models import UserFriendRequest, UserFriend

from utils.core.user import User

@login_required
def profile(us_request, username):
    user = us_request.user

    #### let's get the user based on the uidb36 coming in
    profile      = None
    authorized  = False
    is_user     = False

    if user.username == username:
        profile     = user
        is_user     = True

    context = { 'title': 'My Friends', 'is_user': is_user }
    try:
        ### let's try and get the user
        profile    = User.objects.get(username=username)

        ### is the user looking at his profile?
        if profile == user:
            authorized = True
        else:
            ### nope, is it a possible friend?
            if len(UserFriend.objects.filter(user=user, friend=profile)) or \
                len(UserFriendRequest.objects.filter(user=profile, friend=user)):
                    authorized = True
    except:
        raise Http404

    context['user']     = profile

    context['friends']  = user.get_all_friends()

    UserFriendRequest.objects.update_friend_request_active(user)
    friend_list = us_request.user.friend_user.order_by('friend__first_name')
    friend_request_list = us_request.user.friend_requested.order_by('friend__first_name')

    context.update(friend_list=friend_list, friend_request_list=friend_request_list)
    return render(us_request, "account/user/profile.html", context)

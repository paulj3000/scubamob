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
from django.http import HttpResponseBadRequest, HttpResponse

# define the user data for this account
from scuba.accounts.forms import EmailInviteForm
from scuba.accounts.models import UserBuddyRequest


@login_required
def index(us_request, mode=None):
    context = {'page_title': 'Manage Friends'}
    user = us_request.user

    print(user.get_account())

    UserBuddyRequest.objects.update_friend_request_active(user)
    friend_list = us_request.user.friend_user.order_by('friend__first_name')
    friend_request_list = us_request.user.friend_requests.order_by('friend__first_name')

    context.update(friend_list=friend_list, friend_request_list=friend_request_list)
    return render(us_request, "friends/index.html", context)

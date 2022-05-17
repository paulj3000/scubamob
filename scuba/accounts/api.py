from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# define the user data for this account
from scuba.accounts.forms import AccountForm
from scuba.accounts.models import User


@login_required
def poll(us_request):

    retval = {'data': {'items': []}}

    # and now, let's get our alerts...
    # check for user invites
    alerts = 0
    alerts += len(us_request.user.friend_requested.filter(active=1))
    #alerts  += len(us_request.user.account.get().get_active_friend_requests())

    # let's append the alerts
    retval['data']['items'] = [{'alerts': alerts, 'pollrate': 5000 }]

    # render the appropriate template
    return JsonResponse(retval)

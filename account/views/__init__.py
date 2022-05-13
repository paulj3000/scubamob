# Create your views here.
from pprint import pprint
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.conf import settings

# define the user data for this account
from account.forms import AccountForm
from account.models import User


def register(us_request):
    if us_request.POST:
        account_form    = AccountForm(us_request.POST)

        if account_form.is_valid():
            a = account_form.save()

            new_user = authenticate(username=us_request.POST['username'],
                                    password=us_request.POST['password1'])

            # log the user in
            login(us_request, new_user)

            # create the new account
            User.objects.create(user=new_user)

            # and redirect them home
            return redirect('home')

    else:
        # instantiate the user create forms
        account_form    = AccountForm()

    # now let's render everything
    c = {'account_form': account_form}

    return render(us_request, "account/register.html", c)

@login_required
def home(us_request):
    template    = 'home/home.html'

    context     = {}

    # render the appropriate template
    return render(us_request, template, context)

@login_required
def poll(us_request):

    retval  = {'data': { 'items': [] }}

    # and now, let's get our alerts...
    # check for user invites
    alerts  = 0
    alerts  += len(us_request.user.friend_requested.filter(active=1))
    #alerts  += len(us_request.user.account.get().get_active_friend_requests())

    # let's append the alerts
    retval['data']['items']     = [{'alerts': alerts, 'pollrate': 5000 }]

    # render the appropriate template
    return JSONResponse(api_response(**retval))


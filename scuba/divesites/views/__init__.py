# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# define the user data for this account
from scuba.divesites.forms import SiteForm


def index(us_request):

    context = {}

    # render the appropriate template
    return render(us_request, 'divesites/index.html', context)


def site(us_request, url):

    context = {}

    # render the appropriate template
    return render(us_request, 'divesites/index.html', context)


@login_required
def newsite(us_request, siteid=None):
    user = us_request.user
    #if not user.account.can_add_divesites:
    #    raise Http404

    # render the appropriate template
    if us_request.method == 'POST':
        site_form = SiteForm(us_request.POST, user_id=us_request.user.id, site_id=siteid)
        if site_form.is_valid():
            messages.add_message(us_request, messages.INFO, 'Site successfully saved')
            site_form.save()
    elif siteid:
        site_form = SiteForm(user_id=us_request.user.id, site_id=siteid)
        divelog = site_form.findsite(siteid)
    else:
        site_form = SiteForm(user_id=us_request.user.id)

    context = {'site_form': site_form, 'title': 'Create a new Dive Site'}

    return render(us_request, 'divesites/edit.html', context)

# Create your views here.
from pprint import pprint

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.template import RequestContext


@login_required
def settings(us_request, mode, formname):
    account = us_request.user
    context_mode = 'edit%s'

    # render the appropriate template
    if us_request.method == 'POST':
        form = formname(us_request.POST, instance=account)
        if form.is_valid():
            form.save()

        # ok, everything is done.  Let's redirect the user to the home page
        messages.success(us_request, 'Your %s has been updated' % mode)
        return HttpResponseRedirect(reverse('account_settings'))

    else:
        form = formname(instance=account)

    context = { 'form': form, 'mode': mode }
    return render(us_request, "settings/index.html", context)

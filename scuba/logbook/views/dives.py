from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from scuba.logbook.forms import DiveForm


@login_required
def index(us_request):
    # render the appropriate template
    context     = {}
    return render(us_request, 'logbook/index.html', context)


@login_required
def edit(us_request,logid=None):
    # render the appropriate template
    if us_request.method == 'POST':
        dive_form   = DiveForm(us_request.POST, user_id=us_request.user.id, log_id=logid)
        if dive_form.is_valid():
            messages.add_message(us_request, messages.INFO, 'Hello world.')
            dive_form.save()
            return redirect('/logbook/')
    elif logid:
        dive_form   = DiveForm(user_id=us_request.user.id, log_id=logid)
        divelog     = dive_form.findlog(logid)
    else:
        dive_form   = DiveForm(user_id=us_request.user.id)

    context     = { 'dive_form': dive_form }
    context.update(csrf(us_request))

    return render(us_request, 'logbook/edit.html', context)

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages


@login_required
def settings(us_request, mode, formname):
    account = us_request.user

    # render the appropriate template
    if us_request.method == 'POST':
        form = formname(us_request.POST, instance=account)
        if form.is_valid():
            form.save()

        # ok, everything is done.  Let's redirect the user to the home page
        messages.success(us_request, 'Your %s has been updated' % mode)
        return HttpResponseRedirect(reverse('settings_home'))

    else:
        form = formname(instance=account)

    context = {'form': form, 'mode': mode}
    return render(us_request, "settings/index.html", context)

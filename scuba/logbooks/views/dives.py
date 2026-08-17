from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(us_request):
    # render the appropriate template
    context = {}
    return render(us_request, 'logbook/index.html', context)

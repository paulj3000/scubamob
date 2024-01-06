from django.shortcuts import render
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from scuba.diveshops.models import Diveshop


@login_required
def index(us_request):
    # render the appropriate template
    context = {}
    return render(us_request, 'diveshops/index.html', context)


@login_required
def getlocaldiveshops(us_request):
    retval = []

#    try:
    radius = int(us_request.GET['radius'])
    lon = float(us_request.GET['lon'])
    lat = float(us_request.GET['lat'])

    for ds in Diveshop.get_local_diveshops(lon, lat, radius):
        retval.append(ds)

    return JsonResponse({'items': retval})

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
    radius = us_request.GET.get('radius')
    lon = us_request.GET.get('lon')
    lat = us_request.GET.get('lat')

    shops = Diveshop.get_local_diveshops(lon, lat, radius)

    retval = [
        {
            'id': shop.pk_as_str,
            'name': shop.name,
            'lat': float(shop.lat),
            'long': float(shop.long),
        }
        for shop in shops
    ]

    return JsonResponse({'items': retval})

from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from scuba.diveshops.mongo import DiveShop as DiveShopMongo


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
    dsmongo = DiveShopMongo()

    for ds in dsmongo.get_local_diveshops(lon, lat, radius):
        retval.append(ds)

    return JSONResponse(api_response(data={ 'items' : retval }))

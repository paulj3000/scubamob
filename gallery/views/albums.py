from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pprint import pprint
from django.core.urlresolvers import reverse

from logbook.forms import DiveForm 
from utils.jsonresponse import JSONResponse
from gallery.models import Album


@login_required
def index(us_request):
    ## render the appropriate template
    context     = {}
    return render(us_request, 'gallery/index.html', context)

@login_required
@require_http_methods(["GET"])
def showalbum(us_request, id):
    pprint(us_request.user.albums.filter())

    retval  = []
    for album in us_request.user.albums.filter():
        json    = album.to_json()
        json['url'] =   reverse('show_album', kwargs={'id': json['id']})
        retval.append(json)

    return JSONResponse({'albums': retval })

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def json_createalbum(us_request):
    params = us_request.REQUEST

    retval  = []

    try:
        ## convert the response to JSON
        Album.objects.create(account=us_request.user, title=params['title'], description=params.get('description'))


        return JSONResponse({'sites': retval })
        
    except:
        raise
        pass

@login_required
@require_http_methods(["GET"])
def json_getalbums(us_request, image_id):
    pprint(us_request.user.albums.filter())

    retval  = []
    for album in us_request.user.albums.filter():
        json    = album.to_json()
        json['url'] =   reverse('show_album', kwargs={'id': json['id']})
        retval.append(json)

    return render(us_request, 'gallery/image.html', context)

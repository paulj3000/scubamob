from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pprint import pprint
from django.core.urlresolvers import reverse

from logbook.forms import DiveForm 
from utils.jsonresponse import JSONResponse, api_response
from gallery.models import Album, AlbumImage


@login_required
def index(us_request):
    ## render the appropriate template
    context     = {}
    return render(us_request, 'gallery/index.html', context)

@login_required
@require_http_methods(["GET"])
def showalbum(us_request, id):
    pprint(us_request.user.albums.all())

    retval  = []

    for album in us_request.user.albums.all():
        json    = album.to_json()
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
        album = Album.objects.create(user=us_request.user, title=params['title'], 
                description=params.get('description'), )

        json    = album.to_json()
        json['url'] =   reverse('show_album', kwargs={'album_id': album.guid})

        return JSONResponse( json )
    except:
        pass

@login_required
@require_http_methods(["GET"])
def json_getalbums(us_request):
    pprint(us_request.user.albums.filter())

    retval  = []
    for album in us_request.user.albums.filter():
        json    = album.to_json()
        json['url'] =   reverse('show_album', kwargs={'album_id': album.guid})

        try:
            json['cover'] =   album.album_image.all().first().thumbnail
        except:
            pass

        img_count   = album.album_image.all().count()
        json['image_count'] =   "%i %s" % (img_count, 'photo' if img_count == 1 else 'photos')
        retval.append(json)

    return JSONResponse({'albums': retval })

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def json_deletealbum(us_request, album_id):
    params = us_request.REQUEST

    retval  = []
    try:
        ## convert the response to JSON
        album = Album.objects.filter(guid=album_id, user=us_request.user).delete()
    except:
        pass

    return JSONResponse( retval )

@login_required
@require_http_methods(['GET'])
def json_getalbumimages(us_request, album_id):
    params = us_request.REQUEST

    #PRODUCTION_GALLERY_URL
    retval  = []
    try:
        ## convert the response to JSON
        print "album id:  %s " % album_id
        images = AlbumImage.objects.filter(album__guid=album_id, album__user=us_request.user)

        for i in images:
            retval.append({ 'thumbnail': i.get_thumbnail(), 'image': i.get_image() })
    except:
        raise
        pass

    return JSONResponse(api_response(data={'items':retval, 'total': len(retval) }))


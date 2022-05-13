from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib import messages

from gallery.models import Album


@login_required
def index(us_request):
    # render the appropriate template
    context = {}
    pprint(us_request.user.id)
    return render(us_request, 'gallery/index.html', context)


@login_required
def showalbum(us_request, album_id):
    # render the appropriate template
    album = get_object_or_404(Album, guid=album_id)

    if not album or album.user != us_request.user:
        raise Http404

    context = { 'album': album }
    return render(us_request, 'gallery/album.html', context)

@login_required
def editalbum(us_request, album_id):
    # render the appropriate template
    album = get_object_or_404(Album, guid=album_id)

    if not album or album.user != us_request.user:
        raise Http404

    context = {'album': album}
    return render(us_request, 'gallery/edit.html', context)

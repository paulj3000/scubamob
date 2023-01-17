from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse

from logbook.forms import DiveForm
from scuba.galleries.models import Album


@login_required
def index(us_request):
    # render the appropriate template
    context = {}
    return render(us_request, 'galleries/index.html', context)


@login_required
@require_http_methods(["GET"])
def showalbum(us_request, id):
    retval = []
    for album in us_request.user.albums.filter():
        json = album.to_json()
        json['url'] = reverse('show_album', kwargs={'id': json['id']})
        retval.append(json)

    return JsonResponse({'albums': retval})


@login_required
@require_http_methods(["POST"])
def json_createalbum(us_request):
    params = us_request.REQUEST

    retval = []
    # convert the response to JSON
    Album.objects.create(account=us_request.user, title=params['title'], description=params.get('description'))
    retval = []
    for album in us_request.user.albums.filter():
        json = album.to_json()
        json['url'] = reverse('show_album', kwargs={'id': json['id']})
        retval.append(json)

    return render(us_request, 'galleries/image.html', context)

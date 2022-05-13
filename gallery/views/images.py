import uuid

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pprint import pprint
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

#from boto.s3.connection import S3Connection
from PIL import Image

from logbook.forms import DiveForm
from utils.core.user import User
from gallery.models import Album, AlbumImage


IMAGE_TYPE_EXTENSIONS   = {
        'image/gif': 'gif',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/tiff': 'tiff'
}


@login_required
@require_http_methods(["POST"])
def upload(us_request):
    params = us_request.REQUEST

    account = us_request.user.get_account()

    retval  = {'data': { 'items': [] }}

    try:
        ## convert the response to JSON
        album_id        = params['albumId']
        uploaded_image  = us_request.FILES['image']

        ##  let's get the album
        album   = us_request.user.get_album_by_guid(album_id)
        gallery_file                = album.add_image(uploaded_image)
        gallery_file_thumbnail      = album.add_image_thumbnail(uploaded_image)

        retval['data']['items'] = [{ 'thumbnail': gallery_file_thumbnail, 'full': gallery_file }]
        AlbumImage.objects.create(album=album, image=gallery_file, thumbnail=gallery_file_thumbnail)
    except:
        raise

    return JSONResponse(api_response(**retval))

@login_required
@require_http_methods(["GET"])
def getimage(us_request):
    params = us_request.REQUEST

    account = us_request.user.get_account()

    retval  = {'data': { 'items': [] }}

    return JSONResponse(api_response(**retval))

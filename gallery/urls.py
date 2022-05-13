# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path, re_path

import gallery.views as gallery_views
import gallery.views.images as gallery_images
import gallery.views.json as gallery_json


urlpatterns = [
    path('', gallery_views.index,name="gallery_home"),
    re_path(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})/edit/?$', gallery_views.editalbum, name="edit_album"),
    re_path(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})$', gallery_views.showalbum, name="show_album"),

    path('albums/image/upload', gallery_images.upload, name="gallery_image_upload"),

    re_path(r'json/deletealbum/(?P<album_id>[0-9A-Fa-f-]{32,36})$', gallery_json.json_deletealbum, name='delete_album'),
    path('json/createalbum/', gallery_json.json_createalbum),
    path('json/getalbums/', gallery_json.json_getalbums, name="json_getalbums"),

    re_path(r'json/getalbumimages/(?P<album_id>[0-9A-Fa-f-]{32,36})$', gallery_json.json_getalbumimages, name="json_getalbumimages"),
]

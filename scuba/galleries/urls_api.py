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

import scuba.galleries.api as galleries_api


urlpatterns = [
    re_path(r'deletealbum/(?P<album_id>[0-9A-Fa-f-]{32,36})$',
        galleries_api.json_deletealbum,
        name='delete_album'),
    path('createalbum/',
        galleries_api.json_createalbum),
    path('albums',
        galleries_api.ListAlbumsApi.as_view(),
        name="api_listalbums"),

    re_path(r'getalbumimages/(?P<album_id>[0-9A-Fa-f-]{32,36})$',
        galleries_api.json_getalbumimages,
        name="json_getalbumimages"),
]

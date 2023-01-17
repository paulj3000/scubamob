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

import scuba.galleries.views as galleries_views
import scuba.galleries.views.images as galleries_images


urlpatterns = [
    path('', galleries_views.index, name="galleries_home"),
    re_path(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})/edit/?$', galleries_views.editalbum, name="edit_album"),
    re_path(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})$', galleries_views.showalbum, name="show_album"),

    path('albums/image/upload', galleries_images.upload, name="galleries_image_upload"),
]

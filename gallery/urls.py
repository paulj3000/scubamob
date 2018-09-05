# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook. 
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'gallery.views.index',name="gallery_home"),
    url(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})/edit/?$', 'gallery.views.editalbum',name="edit_album"),
    url(r'albums/(?P<album_id>[0-9A-Fa-f-]{32,36})$', 'gallery.views.showalbum',name="show_album"),

    url(r'albums/image/upload$', 'gallery.views.images.upload',name="gallery_image_upload"),

    url(r'json/deletealbum/(?P<album_id>[0-9A-Fa-f-]{32,36})$', 'gallery.views.json.json_deletealbum', name='delete_album'),
    url(r'json/createalbum/?$', 'gallery.views.json.json_createalbum'),
    url(r'json/getalbums/?$', 'gallery.views.json.json_getalbums', name="json_getalbums"),
    
    url(r'json/getalbumimages/(?P<album_id>[0-9A-Fa-f-]{32,36})$', 'gallery.views.json.json_getalbumimages', name="json_getalbumimages"),
)

# -----------------------------------------------------------------------------
# account/urls.py
#
# This is the urls.py for all things friends related
#
# (C) Copyright 2014, CalendarReel.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^ajax/invited/?$', 'friends.views.ajax.invited'),
    url(r'^ajax/addfriend/?$', 'friends.views.ajax.add_friend'),
    url(r'^ajax/blockfriend/?$', 'friends.views.ajax.block_friend'),
    url(r'^ajax/cancelrequest/?$', 'friends.views.ajax.cancel_request'),

    url(r'^ajax/acceptrequest/?$', 'friends.views.ajax.accept_request'),
)

# -----------------------------------------------------------------------------
# account/urls.py
#
# This is the urls.py for all things account related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url, include
from django.contrib.auth.views import password_reset

from account.forms import LoginForm, PasswordForm, SettingsForm

urlpatterns = patterns('',
    url(r'^$',          'friends.views.index', name='friends_index'),
#    url(r'^ajax/', include('account.urls_ajax')),
    
    url(r'^json/setfavorite/?$', 'account.views.json.setfavorite', name='setfavorite'),
    url(r'^json/getfavorite/?$', 'account.views.json.getfavorites', name='getfavorites'),

    url(r'^request/accept/?$', 'friends.views.ajax.accept', name='friend_accept'),
    url(r'^invite/?$', 'friends.views.ajax.invite', name='friends_invite'),
)

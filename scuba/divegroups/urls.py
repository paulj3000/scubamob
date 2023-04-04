# -----------------------------------------------------------------------------
# account/urls.py
#
# This is the urls.py for all things account related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import include
from django.urls import path, re_path

#import scuba.divegroups.views.ajax as friends_ajax
import scuba.divegroups.views as friends_views
import scuba.accounts.views.json as account_json


urlpatterns = [
    path('', friends_views.index, name='friends_index'),
#    url(r'^ajax/', include('account.urls_ajax')),

    path('json/setfavorite/', account_json.setfavorite, name='setfavorite'),
    path('json/getfavorite/', account_json.getfavorites, name='getfavorites'),

    #path('request/accept/', friends_ajax.accept, name='friend_accept'),
    #path('invite/', friends_ajax.invite, name='friends_invite'),
]

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
    url(r'^json/setfavorite/?$', 'account.views.json.setfavorite', name='setfavorite'),
    url(r'^json/getfavorite/?$', 'account.views.json.getfavorites', name='getfavorites'),

#    url(r'^invited/?$', 'account.views.friends.index', name='account_friend_invited'),
   
    url(r'^poll/$', 'account.views.poll', name='account_poll'), 
    
    url(r'^settings/', include(patterns('account.views.settings',
        url('^$', 'settings', { 'formname': SettingsForm, 'mode': 'settings' }, name='account_settings' ),
        url('^password/$', 'settings', { 'formname': PasswordForm, 'mode': 'password' }, name='account_settings_password' ),
    ))),
    url(r'^register/$', 'account.views.register', name='account_register'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'account/login.html', 'authentication_form': LoginForm }, name="account_login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^password/sent/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'account/password_reset_done.html'} ),
    url(r'^password/reset/$', password_reset, {'template_name': 'account/password_reset.html', 'email_template_name': 'account/password_reset_email.html'}, name='forgot_password1'),
    url(r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'account/password_reset_done.html'}, name='password_reset_done'),
    url(r'^password_reset_done/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name' : 'account/password_reset_done.html',  'post_reset_redirect': '/account/logout/' }),
)

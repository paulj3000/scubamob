from django.conf.urls import include
from django.urls import path, re_path

from account.forms import SettingsForm
import account.views.json as json_views
import account.views as account_views


urlpatterns = [
    path('json/setfavorite/', json_views.setfavorite, name='setfavorite'),
    path('json/getfavorite/', json_views.getfavorites, name='getfavorites'),

#    url(r'^invited/?$', 'account.views.friends.index', name='account_friend_invited'),

    path('poll/', account_views.poll, name='account_poll'),

    #path('settings/', include(patterns('account.views.settings',
    #    path('', 'settings', { 'formname': SettingsForm, 'mode': 'settings' }, name='account_settings' ),
    #    path('password/', 'settings', { 'formname': PasswordForm, 'mode': 'password' }, name='account_settings_password' ),
    #))),
    path('register/', account_views.register, name='account_register'),
]

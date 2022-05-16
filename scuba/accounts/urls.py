from django.conf.urls import include
from django.urls import path, re_path

from scuba.accounts.forms import SettingsForm, PasswordForm
import scuba.accounts.views.json as json_views
import scuba.accounts.views as account_views
import scuba.accounts.views.settings as settings_views


urlpatterns = [
    path('json/setfavorite/', json_views.setfavorite, name='setfavorite'),
    path('json/getfavorite/', json_views.getfavorites, name='getfavorites'),

#    url(r'^invited/?$', 'account.views.friends.index', name='account_friend_invited'),

    path('poll/', account_views.poll, name='account_poll'),

    path('settings/', include(
        [
            path('', settings_views.settings,
                {'formname': SettingsForm, 'mode': 'settings'},
                name='account_settings'),
            path('password/', settings_views.settings,
                {'formname': PasswordForm, 'mode': 'password'},
                name='account_settings_password'),
        ])),
    path('register/', account_views.register, name='account_register'),
]

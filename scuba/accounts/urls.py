from django.conf.urls import include
from django.urls import path, re_path

from scuba.accounts.forms import SettingsForm, PasswordForm
import scuba.accounts.views.json as json_views
import scuba.accounts.views as account_views
import scuba.accounts.api as account_api
import scuba.accounts.views.settings as settings_views


urlpatterns = [
    path('json/setfavorite/', json_views.setfavorite, name='setfavorite'),
    path('json/getfavorite/', json_views.getfavorites, name='getfavorites'),

#    url(r'^invited/?$', 'account.views.friends.index', name='account_friend_invited'),

    path('poll/', account_api.poll, name='account_poll'),

    path('register/', account_views.register, name='account_register'),
]

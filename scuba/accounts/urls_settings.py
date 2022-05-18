from django.urls import path, re_path

import scuba.accounts.views.settings as settings_views
from scuba.accounts.forms import SettingsForm, PasswordForm


urlpatterns = [
    path('', settings_views.settings,
        {'formname': SettingsForm, 'mode': 'settings'},
        name='account_settings'),
    path('account', settings_views.settings,
        {'formname': SettingsForm, 'mode': 'settings'},
        name='settings_account'),
    path('password/', settings_views.settings,
        {'formname': PasswordForm, 'mode': 'password'},
        name='account_settings_password'),
]

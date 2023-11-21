from django.urls import path, re_path
from django.views.generic import TemplateView

import scuba.accounts.views.settings as settings_views
from scuba.accounts.forms import SettingsForm, PasswordForm


urlpatterns = [
    path('',
         TemplateView.as_view(template_name="settings/index.html"),
         name='settings_home'),
    path('account', settings_views.settings,
         {'formname': SettingsForm, 'mode': 'settings'},
         name='settings_account'),
    path('password/', settings_views.settings,
         {'formname': PasswordForm, 'mode': 'password'},
         name='account_settings_password'),
    path('category/account',
         TemplateView.as_view(template_name="settings/index.html")),
    path('item/display-mode',
         TemplateView.as_view(template_name="settings/index.html")),
    path('item/basic-info',
         TemplateView.as_view(template_name="settings/index.html")),
    path('category/sign-in-and-security',
         TemplateView.as_view(template_name="settings/index.html")),
    path('item/manage-email-addresses',
         TemplateView.as_view(template_name="settings/index.html"))
]

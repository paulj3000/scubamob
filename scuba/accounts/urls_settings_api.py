from django.urls import path, re_path
from django.views.generic import TemplateView

import scuba.accounts.apis.settings as settings_api


urlpatterns = [
    re_path('emails/(?P<id>[a-fA-F0-9]+)/',
        settings_api.RemoveEmailApi.as_view()
    ),
    re_path('emails/setprimary',
        settings_api.SetPrimaryEmailObjectApi.as_view()),
    path('emails/', settings_api.UserEmailApi.as_view()),
    re_path('list/general',
        settings_api.UserGeneralSettingListApi.as_view()),
    re_path('list/options', settings_api.UserSettingApi.as_view()),
    re_path('list', settings_api.UserSettingListApi.as_view()),
    re_path('(?P<setting>[\w-]+)', settings_api.UserSettingApi.as_view()),
]

from django.urls import path, re_path

import scuba.accounts.apis.settings as settings_api
import scuba.accounts.apis.profile_image as profile_image_api


urlpatterns = [
    re_path(
        'emails/(?P<id>[a-fA-F0-9]+)/',
        settings_api.RemoveEmailApi.as_view()
    ),
    re_path('emails/setprimary',
            settings_api.SetPrimaryEmailObjectApi.as_view()),
    path('emails/', settings_api.UserEmailApi.as_view()),
    path('profile-image/', profile_image_api.ProfileImageApi.as_view()),
    re_path('list/general',
            settings_api.UserGeneralSettingListApi.as_view()),
    re_path('list/options', settings_api.UserSettingApi.as_view()),
    re_path('list', settings_api.UserSettingListApi.as_view()),
    re_path(r'(?P<setting>[\w-]+)', settings_api.UserSettingApi.as_view()),
]

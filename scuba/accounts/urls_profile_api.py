from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.profile as profile_api


urlpatterns = [
    path('', profile_api.GetProfileApi.as_view()),
]

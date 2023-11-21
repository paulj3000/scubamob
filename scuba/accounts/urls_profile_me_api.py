from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.profile as profile_api


urlpatterns = [
    path('checkins', profile_api.GetCheckinsApi.as_view()),
]

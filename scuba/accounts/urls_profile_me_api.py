from django.urls import path

import scuba.accounts.apis.profile as profile_api


urlpatterns = [
    path('checkins', profile_api.GetCheckinsApi.as_view()),
]

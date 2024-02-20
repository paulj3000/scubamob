from django.urls import path

import scuba.system.apis as system_apis


urlpatterns = [
    path('cicd/build', system_apis.BuildAPI.as_view()),
]

from django.urls import path

import scuba.home.apis as home_apis


urlpatterns = [
    path('', home_apis.GetHomescreenApi.as_view()),
]

from django.urls import path

import scuba.home.apis as home_apis


urlpatterns = [
    path('', home_apis.GetHomescreenApi.as_view()),
    path('jumbotron/', home_apis.GetJumbotronApi.as_view()),
    path('gallery/daily', home_apis.GetDailyPicApi.as_view())
]

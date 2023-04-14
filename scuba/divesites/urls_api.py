from django.urls import path, re_path

import scuba.divesites.apis as divesite_apis


urlpatterns = [
    path('', divesite_apis.DivesiteListApi.as_view()),
    path(
        'getlocaldivesites',
        divesite_apis.DivesiteListApi.as_view()
    ),
    re_path(r'^([0-9A-Fa-f-]{32,36})$', divesite_apis.DivesiteListApi.as_view()),
    re_path(r'^([0-9A-Fa-f-]{32,36})/reviews/', divesite_apis.AddReviewApi.as_view()),
    re_path(r'^([0-9A-Fa-f-]{32,36})/follow/', divesite_apis.FollowingApi.as_view()),
]

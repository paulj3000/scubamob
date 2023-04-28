from django.urls import path, re_path

import scuba.divesites.apis as divesite_apis


urlpatterns = [
    path('', divesite_apis.DivesiteListApi.as_view()),
    path(
        'getlocaldivesites',
        divesite_apis.DivesiteListApi.as_view()
    ),
    re_path(r'^([0-9A-Fa-f-]{32,36})$', divesite_apis.GetDivesiteApi.as_view()),
    re_path(r'^([0-9A-Fa-f-]{32,36})/reviews/', divesite_apis.AddReviewApi.as_view()),
    re_path(r'^([0-9A-Fa-f-]{32,36})/favorite/', divesite_apis.FavoriteApi.as_view()),
    re_path(r'^([0-9A-Fa-f-]{32,36})/checkin/', divesite_apis.CheckinApi.as_view()),
    re_path(r'checkins/([0-9A-Fa-f-]{32,36})/thank/', divesite_apis.CheckinThankApi.as_view()),
    re_path(r'favorites', divesite_apis.FavoriteListApi.as_view()),
]

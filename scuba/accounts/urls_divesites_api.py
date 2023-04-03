from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.divesites as divesites_api

urlpatterns = [
    path('favorites/', divesites_api.UserDivesiteFavoriteListApi.as_view()),
    re_path(r'favorites/(?P<id>[0-9a-fA-F]{32})/', divesites_api.UserDivesiteFavoriteApi.as_view()),
]

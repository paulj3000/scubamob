from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.divesites as divesites_api


urlpatterns = [
    path('createuser/', divesites_api.UserFavoriteDivesite.as_view()),
]

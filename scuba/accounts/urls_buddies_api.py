from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.buddies as buddies_api


urlpatterns = [
    path('', buddies_api.GetBuddiesListApi.as_view()),
    path('add/', buddies_api.AddBuddyApi.as_view()),
    path('status', buddies_api.BuddyStatusApi.as_view()),
    path('block/', buddies_api.BlockUserApi.as_view()),
    path('requests/', buddies_api.BuddyRequestListApi.as_view()),
    re_path(r'requests/(?P<id>[0-9a-fA-F]{32})/accept', buddies_api.AcceptBuddyRequestApi.as_view()),
    re_path(r'requests/(?P<id>[0-9a-fA-F]{32})/', buddies_api.BuddyRequestApi.as_view()),
]

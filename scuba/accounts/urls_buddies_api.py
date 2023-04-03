from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.buddies as buddies_api


urlpatterns = [
    path('', buddies_api.GetBuddiesListApi.as_view()),
    path('add/', buddies_api.AddBuddyApi.as_view()),
    path('status', buddies_api.BuddyStatusApi.as_view()),
    path('block', buddies_api.BlockUserApi.as_view()),
    path('cancel', buddies_api.CancelBuddyRequestApi.as_view()),
    path('confirm', buddies_api.ConfirmBuddyRequestApi.as_view()),
    path('status', buddies_api.GetBuddyStatusApi.as_view()),
]

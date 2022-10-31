from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.buddies as buddies_api


urlpatterns = [
    path('', buddies_api.GetBuddiesApi.as_view()),
    path('status', buddies_api.BuddyStatusApi.as_view()),
    path('block', buddies_api.BlockUserApi.as_view()),
    path('buddy/add', buddies_api.AddBuddyApi.as_view()),
    path('buddy/cancel', buddies_api.CancelBuddyRequestApi.as_view()),
    path('buddy/confirm', buddies_api.ConfirmBuddyRequestApi.as_view()),
    path('buddy/status', buddies_api.GetBuddyStatusApi.as_view()),
]

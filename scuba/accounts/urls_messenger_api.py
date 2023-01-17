from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.chat as chat_api


urlpatterns = [
    path('users', chat_api.UserListApi.as_view()),
]

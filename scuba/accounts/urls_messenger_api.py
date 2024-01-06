from django.urls import path

import scuba.accounts.apis.chat as chat_api


urlpatterns = [
    path('users', chat_api.UserListApi.as_view()),
]

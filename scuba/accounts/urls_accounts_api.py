from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis as account_api
import scuba.accounts.apis.chat as chat_api


urlpatterns = [
    path('socket', account_api.SocketApi.as_view()),
    path('chats/', chat_api.ChatWUserApi.as_view()),
    path('chats', chat_api.ChatWUserApi.as_view()),
    path('alerts', account_api.AlertsApi.as_view())
]

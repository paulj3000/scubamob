from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.admin_chat as chat_api


urlpatterns = [
    path('all', chat_api.GetAllChatsApi.as_view()),
]

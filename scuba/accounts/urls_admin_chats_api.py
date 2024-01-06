from django.urls import path

import scuba.accounts.apis.admin_chat as chat_api


urlpatterns = [
    path('all', chat_api.GetAllChatsApi.as_view()),
]

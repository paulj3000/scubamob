from django.urls import path

import scuba.accounts.apis.chat as chat_api


urlpatterns = [
    path('messages', chat_api.GetChatMessagesApi.as_view()),
    path('upload', chat_api.UploadFileApi.as_view()),
    path('all', chat_api.GetAllChatsApi.as_view()),
    path('', chat_api.GetChatsApi.as_view())
]

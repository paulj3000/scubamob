from django.urls import path

import scuba.accounts.apis.socket as socket_api


urlpatterns = [
    path('socket/', socket_api.SocketApi.as_view()),
]

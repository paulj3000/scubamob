from django.urls import path

import scuba.accounts.apis as account_api


urlpatterns = [
    path('socket/', account_api.SocketApi.as_view()),
]

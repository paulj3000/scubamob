from django.urls import path

import scuba.accounts.apis.account as account_api
import scuba.accounts.apis.socket as socket_api


urlpatterns = [
    path('socket', socket_api.SocketApi.as_view()),
    path('alerts', socket_api.AlertsApi.as_view()),
    path('reviews', account_api.GetReviewsApi.as_view())
]

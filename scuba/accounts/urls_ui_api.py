from django.urls import path

import scuba.accounts.apis.ui as ui_api


urlpatterns = [
    path('message', ui_api.AddUIMessageApi.as_view()),
]

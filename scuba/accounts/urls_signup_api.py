from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.signup as signup_api


urlpatterns = [
    path('confirmation_code', signup_api.ConfirmationCode.as_view()),
    path('password', signup_api.SetPassword.as_view()),
    path('username', signup_api.SetUsername.as_view()),
]

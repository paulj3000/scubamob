from django.urls import path

import scuba.accounts.apis.signup as signup_api


urlpatterns = [
    path('confirmation_code/', signup_api.ConfirmationCode.as_view()),
    path('confirmation_code', signup_api.ConfirmationCode.as_view()),
    path('password/', signup_api.SetPasswordApi.as_view()),
    path('username/', signup_api.SetUsernameApi.as_view()),
    path('createuser/', signup_api.CreateUserApi.as_view()),
]

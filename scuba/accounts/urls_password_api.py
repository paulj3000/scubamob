from django.urls import path, re_path
import scuba.accounts.apis.password as password_api


urlpatterns = [
    path('reset/', password_api.PasswordResetApi.as_view())
]

from django.urls import path, re_path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


urlpatterns = [
    path('reset/',
         PasswordResetView.as_view(template_name='accounts/password_reset.html',),
         name='forgot_password'),

    path('password_reset_done/',
        PasswordResetDoneView\
            .as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),

    re_path(r'password_reset_done/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/',
        PasswordResetConfirmView\
            .as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),

    path('reset/done/',
        PasswordResetCompleteView\
            .as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
]

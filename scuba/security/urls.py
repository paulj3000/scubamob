from django.urls import path

import scuba.security.apis as security_apis


urlpatterns = [
    path('emails/bounced', security_apis.BouncedEmailsAPI.as_view()),
]

from django.urls import re_path

import scuba.accounts.iapis.settings as settings_iapi


urlpatterns = [
    re_path('validate/(?P<id>[0-9a-fA-F]+)', settings_iapi.ValidateUserId.as_view()),
]

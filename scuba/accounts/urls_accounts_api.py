from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.api as account_api


urlpatterns = [
    path('/poll', account_api.poll, name='account_poll'),
]

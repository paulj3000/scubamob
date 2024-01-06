from django.urls import re_path

import scuba.accounts.apis.feed as feed_api


urlpatterns = [
    re_path(r'(?P<id>[0-9a-fA-F]{32})', feed_api.GetFeedApi.as_view()),
    re_path(r'(?P<id>[0-9a-fA-F]{32})/flag', feed_api.FlagApi.as_view()),
]

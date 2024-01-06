from django.urls import path, re_path

import scuba.accounts.apis.collections as collections_api


urlpatterns = [
    path('', collections_api.CollectionListCreateApi.as_view()),
    re_path('(?P<id>[a-fA-F0-9]+)/add', collections_api.AddToCollectionApi.as_view())
]

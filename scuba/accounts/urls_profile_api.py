from django.conf.urls import include
from django.urls import path, re_path

import scuba.accounts.apis.profile as profile_api


urlpatterns = [
    path('', profile_api.GetProfileApi.as_view()),
    path('follow', profile_api.FollowProfileApi.as_view()),
    path('media', profile_api.GetGalleryApi.as_view()),
    path('feed', profile_api.GetFeedApi.as_view()),
    path('buddies', profile_api.GetBuddiesListApi.as_view()),
    path('albums', profile_api.GetAlbumsApi.as_view()),
    path('photos', profile_api.GetPhotosApi.as_view()),
]

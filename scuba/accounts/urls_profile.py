from django.urls import path, re_path
import scuba.accounts.views.profiles as profile_view


urlpatterns = [
    path('buddies', profile_view.ProfileView.as_view(), name='buddies'),
    path('about', profile_view.ProfileView.as_view(), name='about'),
    path('', profile_view.ProfileView.as_view(), name='profile'),
]

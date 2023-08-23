from django.urls import path, re_path
import scuba.accounts.views.profiles as profile_view


urlpatterns = [
    re_path(r'(?P<username>[\w]+)$', profile_view.ProfileView.as_view(), name='profile'),
    re_path(r'(?P<username>[\w]+)/buddies$', profile_view.ProfileView.as_view(), name='buddies'),
    re_path(r'(?P<username>[\w]+)/about$', profile_view.ProfileView.as_view(), name='about'),
]

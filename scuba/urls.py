from django.conf.urls import include
from django.urls import path, re_path
from django.views.generic import TemplateView

from django.contrib.auth.views import LogoutView

import scuba.settings
import scuba.home.views as home_views
import scuba.home.apis as home_apis
import scuba.accounts.views.profiles as account_profiles
import scuba.accounts.views.login as login_views
import scuba.accounts.views.signup as signup_views
import scuba.accounts.views as account_views
import scuba.accounts.apis.account as account_api
import scuba.accounts.apis.profile as profile_api

from scuba.sitesettings.apis import GetSystemSettingsApi, GetSystemEndpointsApi


from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^scubamob/', include('scubamob.foo.urls')),
    path('', home_views.IndexView.as_view(), name='index'),

    path('home/', home_views.HomeView.as_view(), name='home'),
    path('signup/', signup_views.SignupView.as_view(), name='signup'),

    path('account/', include('scuba.accounts.urls')),
    path('settings/', include('scuba.accounts.urls_settings')),
    #path('friends/', include('scuba.friends.urls')),
    path('groups/', include('scuba.divegroups.urls')),
    path('logbooks/', include('scuba.logbooks.urls')),
    path('divesites/', include('scuba.divesites.urls')),
    path('diveshops/', include('scuba.diveshops.urls')),
    path('gallery/', include('scuba.galleries.urls')),
    path('equipment/', include('scuba.equipment.urls')),
    path('env/', include('scuba.environ.urls')),

    path('password/', include('scuba.accounts.urls_password')),

    #url(r'^profile/', include('scuba.accounts.urls_profile')),

    #path('api/1.0/divelogs/', include('api.urls_divelogs')),
    #path('api/1.0/diveshops/', include('api.urls_diveshops')),

    #path('api/1.0/mobile/account', include('api.urls_account')),
    path('api/accounts/', include('scuba.accounts.urls_accounts_api')),
    path('api/password/', include('scuba.accounts.urls_password_api')),
    path('api/signup/', include('scuba.accounts.urls_signup_api')),
    path('api/profile/', profile_api.GetMeProfileApi.as_view()),
    re_path('api/profile/(?P<id>[a-fA-F0-9]+)/', include('scuba.accounts.urls_profile_api')),
    path('api/buddies/', include('scuba.accounts.urls_buddies_api')),
    path('api/logbooks/', include('scuba.logbooks.urls_logbooks_api')),
    path('api/ui/', include('scuba.accounts.urls_ui_api')),
    path('api/chats/', include('scuba.accounts.urls_chats_api')),
    path('api/messenger/', include('scuba.accounts.urls_messenger_api')),
    path('api/home/', include('scuba.home.urls_home_api')),
    path('api/galleries/', include('scuba.galleries.urls_api')),
    path('api/divesites/', include('scuba.divesites.urls_api')),
    path('api/search', home_apis.SearchApi.as_view()),
    path('api/settings/', include('scuba.accounts.urls_settings_api')),
    path('api/endpoints', GetSystemEndpointsApi.as_view()),
    path('api/sitesettings', GetSystemSettingsApi.as_view()),
    path('api/sitesettings/all', GetSystemSettingsApi.as_view()),
    path('api/register/', account_api.RegisterUserApi.as_view()),
    path('api/login/', account_api.LoginUserApi.as_view()),

    path('iapi/settings/', include('scuba.accounts.urls_settings_iapi')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # start the messenger portion of the show
    path('messenger/new',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),
    path('messenger',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),

    re_path('messenger/t/(?P<id>[a-fA-F0-9]+)',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),

    # let's go ahead and add some static pages (about and all of those things....)
    path('terms/', TemplateView.as_view(template_name="static/terms.html")),
    path('aboutus/', TemplateView.as_view(template_name="static/about.html")),
    path('privacy/', TemplateView.as_view(template_name="static/privacy.html"), name='privacy_policy'),

    # start the legal stuff
    #path('privacy', content_views.ContentView.as_view(), name='privacy'),
    #path('terms', content_views.ContentView.as_view(), name='terms'),
    #path('cookies', content_views.ContentView.as_view(), name='cookies'),
    #path('about', content_views.ContentView.as_view(), name='about'),

    # start some user account helper modules

    path('login/', login_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name="logout"),

    path('robots.txt', include('scuba.robots.urls')),

    # enable the admin section
    path('admin/', admin.site.urls),

    #re_path(r'^p/(?P<username>[\w_]+)/buddies$',
    #    account_profiles.BuddiesView.as_view(),
    #    name='buddies'),
    #re_path(r'^p/(?P<username>[\w_]+)/$',  account_profiles.profile, name='profile'),
    re_path(r'^p/(?P<username>[\w_]+)/',  include('scuba.accounts.urls_profile')),
]

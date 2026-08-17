from django.conf.urls import include
from django.urls import path, re_path
from django.views.generic import TemplateView

from django.contrib.auth.views import LogoutView

import scuba.home.views as home_views
import scuba.search.views as search_views
import scuba.home.apis as home_apis
import scuba.accounts.views.login as login_views
import scuba.accounts.views.signup as signup_views
import scuba.accounts.views.impersonation as impersonation_views
import scuba.content.views as content_views
import scuba.accounts.apis.account as account_api
import scuba.accounts.apis.profile as profile_api

from scuba.settings import SITE_TITLE

from django.contrib import admin
admin.autodiscover()

admin.site.site_title = SITE_TITLE
admin.site.site_header = f"{SITE_TITLE} - Admin Section"


urlpatterns = [
    # Examples:
    # url(r'^scubamob/', include('scubamob.foo.urls')),
    path('', home_views.IndexView.as_view(), name='index'),

    path('home/', home_views.HomeView.as_view(), name='home'),
    path('signup/', signup_views.SignupView.as_view(), name='signup'),
    path('impersonate/stop/', impersonation_views.StopImpersonationView.as_view(), name='stop_impersonation'),
    path('security/', include('scuba.security.urls')),
    path('aws/', include('scuba.aws.urls')),

    path('collections/', include('scuba.accounts.urls_collections')),
    path('search', search_views.SearchView.as_view(), name='search'),
    path('articles/', include('scuba.content.urls_articles')),
    path('account/', include('scuba.accounts.urls')),
    path('settings/', include('scuba.accounts.urls_settings')),
    path('logbooks/', include('scuba.logbooks.urls')),
    path('sites/', include('scuba.divesites.urls')),
    path('diveshops/', include('scuba.diveshops.urls')),
    path('gallery/', include('scuba.galleries.urls')),
    path('equipment/', include('scuba.equipment.urls')),
    path('env/', include('scuba.environ.urls')),

    path('password/', include('scuba.accounts.urls_password')),

    # start the legal stuff
    path('privacy', content_views.ContentView.as_view(), name='privacy'),
    path('terms', content_views.ContentView.as_view(), name='terms'),
    path('cookies', content_views.ContentView.as_view(), name='cookies'),
    path('about', content_views.ContentView.as_view(), name='about'),
    path('faq', content_views.FAQView.as_view(), name='faq'),

    path('api/accounts/', include('scuba.accounts.urls_accounts_api')),
    path('api/buddies/', include('scuba.accounts.urls_buddies_api')),
    path('api/collections/', include('scuba.accounts.urls_collections_api')),
    path('api/user/divesites/', include('scuba.accounts.urls_divesites_api')),
    path('api/password/', include('scuba.accounts.urls_password_api')),
    path('api/signup/', include('scuba.accounts.urls_signup_api')),
    path('api/profile/me', profile_api.GetMeProfileApi.as_view()),
    path('api/profile/me/', include('scuba.accounts.urls_profile_me_api')),
    path('api/profile/q/', profile_api.QueryApi.as_view()),
    re_path('api/profile/(?P<id>[a-fA-F0-9]{32})/', include('scuba.accounts.urls_profile_api')),
    path('api/ui/', include('scuba.accounts.urls_ui_api')),
    path('api/feed/', include('scuba.accounts.urls_feed_api')),
    path('api/home/', include('scuba.home.urls_home_api')),
    path('api/galleries/', include('scuba.galleries.urls_api')),
    path('api/divesites/', include('scuba.divesites.urls_api')),
    path('api/search', home_apis.SearchApi.as_view()),
    path('api/settings/', include('scuba.accounts.urls_settings_api')),
    path('api/register/', account_api.RegisterUserApi.as_view()),
    path('api/login/', account_api.LoginUserApi.as_view()),

    path('iapi/settings/', include('scuba.accounts.urls_settings_iapi')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # start the messenger portion of the show
    path(
        'messenger/new',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),
    path(
        'messenger',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),

    re_path(
        'messenger/t/(?P<id>[a-fA-F0-9]+)',
        TemplateView.as_view(template_name="messenger.html"),
        name='messenger',
    ),

    # start some user account helper modules
    path('login/', login_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name="logout"),

    path('login/magic-link/', login_views.MagicLinkRequestView.as_view(), name='magic_link_request'),
    path(
        'login/magic-link/sent/',
        TemplateView.as_view(
            template_name='accounts/magic_link_sent.html',
            extra_context={'hide_nav_account': True},
        ),
        name='magic_link_sent'),
    path(
        'login/magic-link/<str:uidb64>/<str:token>/',
        login_views.MagicLinkConfirmView.as_view(),
        name='magic_link_confirm'),

    path('robots.txt', include('scuba.robots.urls')),

    # enable the admin section
    path('admin/', admin.site.urls),
    path(r'p/', include('scuba.accounts.urls_profile')),
]

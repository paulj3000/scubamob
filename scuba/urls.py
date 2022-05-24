from django.conf.urls import include
from django.urls import path, re_path
from django.views.generic import TemplateView

from django.contrib.auth.views import LoginView, LogoutView


import scuba.settings
import scuba.home.views as home_views
import scuba.accounts.views.profiles as account_profiles
import scuba.accounts.views.login as login_views
import scuba.accounts.views.signup as signup_views
import scuba.accounts.views as account_views


from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^scubamob/', include('scubamob.foo.urls')),
    path('', home_views.IndexView.as_view(), name='index'),

    path('home/', home_views.home, name='home'),
    path('signup/', signup_views.SignupView.as_view(), name='signup'),

    path('account/', include('scuba.accounts.urls')),
    path('settings/', include('scuba.accounts.urls_settings')),
    path('friends/', include('scuba.friends.urls')),
    path('logbook/', include('logbook.urls')),
    path('divesites/', include('divesites.urls')),
    path('diveshops/', include('diveshops.urls')),
    path('gallery/', include('gallery.urls')),
    path('equipment/', include('equipment.urls')),
    path('env/', include('scuba.environ.urls')),
#    url(r'^diveshop/', include('diveshop.urls')),

    path('password/', include('scuba.accounts.urls_password')),

    #url(r'^profile/', include('scuba.accounts.urls_profile')),

    path('api/1.0/divesites/', include('api.urls_divesites')),
    path('api/1.0/divelogs/', include('api.urls_divelogs')),
    path('api/1.0/diveshops/', include('api.urls_diveshops')),

    path('api/1.0/mobile/account', include('api.urls_account')),
    path('api/1.0/mobile', include('api.urls_mobile')),
    path('api/accounts/', include('scuba.accounts.urls_accounts_api')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # let's go ahead and add some static pages (about and all of those things....)
    path('terms/', TemplateView.as_view(template_name="static/terms.html")),
    path('aboutus/', TemplateView.as_view(template_name="static/about.html")),
    path('privacy/', TemplateView.as_view(template_name="static/privacy.html"), name='privacy_policy'),

    # start some user account helper modules

    path('login/', login_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name="logout"),

    # enable the admin section
    path('admin/', admin.site.urls),

    re_path(r'^p/(?P<username>[0-9A-Za-z]+)/$',  account_profiles.profile, name='profile'),
]

from django.conf.urls import include
from django.urls import path, re_path
from django.views.generic import TemplateView

from django.contrib.auth.views import LoginView


import scuba.settings
import home.views as home_views
import account.views.profiles as account_profiles
#import account.views.login as login_views
import account.views.xlogin as login_views
import account.views as account_views


from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^scubamob/', include('scubamob.foo.urls')),
    path('', home_views.index, name='index'),
    path('home/', home_views.home, name='home'),
    path('register/', account_views.register, name='register'),

    path('account/', include('account.urls')),
    path('friends/', include('friends.urls')),
    path('logbook/', include('logbook.urls')),
    path('divesites/', include('divesites.urls')),
    path('diveshops/', include('diveshops.urls')),
    path('gallery/', include('gallery.urls')),
    path('equipment/', include('equipment.urls')),
    path('env/', include('env.urls')),
#    url(r'^diveshop/', include('diveshop.urls')),

    path('password/', include('account.urls_password')),

    #url(r'^profile/', include('account.urls_profile')),

    path('api/1.0/divesites/', include('api.urls_divesites')),
    path('api/1.0/divelogs/', include('api.urls_divelogs')),
    path('api/1.0/diveshops/', include('api.urls_diveshops')),

    path('api/1.0/mobile/account', include('api.urls_account')),
    path('api/1.0/mobile', include('api.urls_mobile')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    ## let's go ahead and add some static pages (about and all of those things....)
    path('terms/', TemplateView.as_view(template_name="static/terms.html")),
    path('aboutus/', TemplateView.as_view(template_name="static/about.html")),
    path('privacy/', TemplateView.as_view(template_name="static/privacy.html"), name='privacy_policy'),

    # start some user account helper modules

    # enable the admin section
    path('admin/', admin.site.urls),

    re_path(r'^(?P<username>[0-9A-Za-z]+)/$',  account_profiles.profile, name='profile'),

    #path('xx/login/', login_views.LoginView.as_view(
    path('xx/login/', LoginView.as_view(
        template_name='account/login.html'),
        name='login'),

    #path('logout/', SignoutView.as_view(next_page='/'), name='signout'),
]

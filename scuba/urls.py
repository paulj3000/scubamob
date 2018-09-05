#pauljames dimitriu
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
import scuba.settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^scubamob/', include('scubamob.foo.urls')),
    url(r'^$',          'home.views.index', name='index'),
    url(r'^home/',     'home.views.home', name='home'),
    #url(r'^register/$', 'home.views.register', name='register'),
    
    #url(r'', include('social_auth.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^friends/', include('friends.urls')),
    url(r'^logbook/', include('logbook.urls')),
    url(r'^divesites/', include('divesites.urls')),
    url(r'^diveshops/', include('diveshops.urls')),
    url(r'^gallery/', include('gallery.urls')),
    url(r'^equipment/', include('equipment.urls')),
    url(r'^env/', include('env.urls')),
#    url(r'^diveshop/', include('diveshop.urls')),
    
    #url(r'^profile/', include('account.urls_profile')),

    url(r'^api/1.0/divesites/', include('api.urls_divesites')),
    url(r'^api/1.0/divelogs/', include('api.urls_divelogs')),
    url(r'^api/1.0/diveshops/', include('api.urls_diveshops')),
    
    url(r'^api/1.0/mobile/account', include('api.urls_account')),
    url(r'^api/1.0/mobile', include('api.urls_mobile')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    ## let's go ahead and add some static pages (about and all of those things....)
    (r'^terms/$',             TemplateView.as_view(template_name="static/terms.html")),
    (r'^aboutus/$',           TemplateView.as_view(template_name="static/about.html")),
    url(r'^privacy/$',        TemplateView.as_view(template_name="static/privacy.html"), name='privacy_policy'),
   
    ### start some user account helper modules

    ### enable the admin section
    url(r'^admin/', include(admin.site.urls)),
   
    url(r'^(?P<username>[0-9A-Za-z]+)/$',  'account.views.profiles.profile', name='profile'),
   
    
    ### this will help define some static stuff
#    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': scuba.settings.GENERATED_MEDIA_DIR}),
)

#urlpatterns += staticfiles_urlpatterns()

#-----------------------------------------------------------------------------
# scuba/settings.py
#
# This is the main settings file for ScubaMob
#
# (C) Copyright 2014, Digital Infinity Sofware.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
import os

import django.conf.global_settings as DEFAULT_SETTINGS

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_ROOT = os.path.join(BASE_DIR, './templates')
IMAGES_ROOT = os.path.join(BASE_DIR, './static/images')
STATIC_ROOT = os.path.join(BASE_DIR, './static')
LOG_DIRECTORY = '/tmp'

TEMPLATE_DIR_LIST = [
    os.path.join(BASE_DIR, './templates'),
    #os.path.join(BASE_DIR, './skmcore/templates'),
]

ADMINS = (
     ('Pauljames Dimitriu', 'paulj1999@yahoo.com'),
)

AUTHENTICATION_BACKENDS =   ('utils.middleware.authentication.DefaultBackend',
                             'utils.middleware.authentication.EmailLogin', )

SERVER_EMAIL = 'no-reply@scubamob.com'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s/db/scubamob' % BASE_DIR ,
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#DATABASE_ROUTERS = ['utils.db.routers.Mongo']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

MONGO   = {
        'USE_REPLICASET': False,
        'HOSTS': [],
        'REPLICASET': {},
        'HOST': 'localhost',
        'PORT': 27017,
        'DATABASE': 'scubamob'
}

NOSQL   = 'mongo'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(ql8jk&amp;4f5y+m+4#5mgk^^^tf)2cb6*x6x&amp;wkw$v626tyaiijm'

YUICOMPRESSOR_PATH = os.path.join(BASE_DIR, './scuba/tools/yuicompressor.jar')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIR_LIST,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'utils.context_processors.sm',
            ],
        },
    },
]

LOGIN_URL = '/login/'

LOGIN_EXEMPT_URLS = (
         r'^about\.html$',
          r'^legal/', # allow any URL under /legal/*
)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '//d1fqxyumeztd89.cloudfront.net/media/'
PRODUCTION_GALLERY_URL  = '//s3-us-west-1.amazonaws.com/scubamob.gallery.dev/'

STATIC_URL  = '/static/'

try:
    from version import *
    PRODUCTION_MEDIA_URL    += '%s/' % RELEASE_VERSION
except ImportError:
    print('no release version available. Continuing with standard settings.')


# add some setting for the
GENERATED_MEDIA_DIR = os.path.join(BASE_DIR, '../_generated_media')
GLOBAL_MEDIA_DIRS = (STATIC_ROOT,IMAGES_ROOT,GENERATED_MEDIA_DIR)


ROOT_URLCONF = 'scuba.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'scuba.wsgi.application'

TEMPLATE_DIRS = (
    TEMPLATE_ROOT,
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'account',
    'gallery',
    'common',
    'divesites',
    'equipment',
    'entities',
    'home',
    'logbook',
    'diveshops',
    'utils',
    'api',
    'friends',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL  = '/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#AUTH_PROFILE_MODULE = "account.Account"
#AUTH_USER_MODEL = 'account.Account'

try:
    from mediasettings import *
except ImportError:
    print('mediasettings.py was not found. Continuing with standard settings.')

WEATHER_UNDERGROUND         = 'weather_underground'
FACEBOOK                    = 'facebook'
GOOGLE_MAPS                 = 'google_maps'
GOOGLE_ADDRESS              = 'google_address'


FACEBOOK_APP_ID             = '178799865530799'
FACEBOOK_API_SECRET         = '502a5c37f483495170f0559afa4ad1ca'

EXTERNAL_INTERFACES = {
    WEATHER_UNDERGROUND: {
        'url': 'http://api.wunderground.com/api/%s/conditions/astronomy/rawtide/q/%s/%s.json',
        'url_latlng': 'http://api.wunderground.com/api/%s/geolookup/conditions/astronomy/rawtide/q/%s,%s.json',
        'method': 'http://api.wunderground.com/api/%s/conditions/q/%s/%s.json',
        'apikey':  'd41784195576cec0',
    },

    FACEBOOK: {
        'app':      '178799865530799',
        'secret':   '502a5c37f483495170f0559afa4ad1ca',
        'url':      'https://graph.facebook.com/oauth/authorize'
    },

    GOOGLE_ADDRESS: {
        'url':      'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false'
    }
}

MEMCACHE = {
    'server':      ['127.0.0.1:11211']
}

# set up the external API stuff
WEATHER_API_KEY = 'd41784195576cec0' + '-'
WEATHER_API_URL = 'http://api.wunderground.com/api/%s/conditions/q/%s/%s.json'
#WEATHER_API_LAT_LNG_URL = 'http://api.wunderground.com/api/%s/conditions/q/%s/%s,%s.json'
WEATHER_API_LAT_LNG_URL = 'http://api.wunderground.com/api/%s/geolookup/conditions/astronomy/rawtide/q/%s,%s.json'

NOSQL_HOST       = 'localhost'
NOSQL_PASSWORD   = 'notset'
NOSQL_PORT       = 27017
NOSQL_DB         = 'scubamob'

#AWS_ACCESS_KEY_ID = 'AKIAJAKVVBLJNXEABZVQ'
#AWS_SECRET_ACCESS_KEY = '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'
AWS_ACCESS_KEY_ID = 'AKIAJDVN6XIBZ5I7TVSA'
AWS_SECRET_ACCESS_KEY = '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'

# Here is the bucket file pattern.  It goes in the following manner:
# account guid / album id / file name
GALLERY_BUCKET      = 'scubamob.gallery.dev'

EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL  = 'no-reply@scubamob.com'
GOOGLE_API_KEY  = 'AIzaSyD8CDOojSGLURvXDISrXKHZss1BkOA-Lss'

# this is a constant to be used to compute geodistance stuff
EARTH_RADIUS    = 3159

# the following settings are for the mobile apps
MOBILE_HEADER_APP   = 'scubaapp'
MOBILE_HEADER_DEVICES   = {'smandroid': 'am', 'smios': 'io'}

try:
    from localsettings import *
except ImportError as ex:
    print('localsettings.py was not loaded. Continuing with standard settings.\n%s' % ex)

MEDIA_DEV_MODE = MEDIA_DEV_MODE if 'MEDIA_DEV_MODE' in locals() else DEBUG

# maxmind settings
#MAXMIND_URL     = 'https://geoip.maxmind.com/geoip/v2.0/city_isp_org/%s'
MAXMIND_URL     = 'https://geoip.maxmind.com/geoip/v2.0/city/%s'
MAXMIND_LICENSE = 'hVeqTCTxxU5H'
MAXMIND_USER    = '75205'
DEBUG_IP        = '68.101.214.253'

# define the mongo collections
MONGO_DIVELOGS		= 'divelogs'


'''
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'app.pipeline.redirect_to_form',
    'app.pipeline.username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'app.pipeline.redirect_to_form2',
    'app.pipeline.first_name',
)
'''


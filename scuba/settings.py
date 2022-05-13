#-----------------------------------------------------------------------------
# scuba/settings.py
#
# This is the main settings file for ScubaMob
#
# (C) Copyright 2014, Digital Infinity Sofware.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from pathlib import Path
import os

import django.conf.global_settings as DEFAULT_SETTINGS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, './static')
LOG_DIRECTORY = '/tmp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=True))

TEMPLATE_ROOT = ''
if DEBUG:
    TEMPLATE_ROOT = os.path.join(f"{BASE_DIR}/templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_ROOT],
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

AUTHENTICATION_BACKENDS = DEFAULT_SETTINGS.AUTHENTICATION_BACKENDS + \
    [
        'rest_framework.authentication.TokenAuthentication',
    ]


SERVER_EMAIL = 'no-reply@scubamob.com'

#MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", f"{BASE_DIR}/db.sqlite3"),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "3306"),
    }
}

REST_FRAMEWORK = {
    'PAGINATE_BY': 2,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'NON_FIELD_ERRORS_KEY': 'errors',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
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
MONGO = {
        'USE_REPLICASET': False,
        'HOSTS': [],
        'REPLICASET': {},
        'HOST': 'localhost',
        'PORT': 27017,
        'DATABASE': 'scubamob'
}

NOSQL = 'mongo'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(ql8jk&amp;4f5y+m+4#5mgk^^^tf)2cb6*x6x&amp;wkw$v626tyaiijm'

YUICOMPRESSOR_PATH = os.path.join(BASE_DIR, './scuba/tools/yuicompressor.jar')

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/home'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PRODUCTION_MEDIA_URL = '//d1fqxyumeztd89.cloudfront.net/media/'
PRODUCTION_GALLERY_URL = '//s3-us-west-1.amazonaws.com/scubamob.gallery.dev/'

STATIC_URL = '/static/'

STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + [
    'compressor.finders.CompressorFinder',
    'yarn.finders.YarnFinder',]

YARN_ROOT_PATH = BASE_DIR

ROOT_URLCONF = 'scuba.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'scuba.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_extensions',
    'compressor',
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
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

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
AUTH_USER_MODEL = 'account.User'

WEATHER_UNDERGROUND = 'weather_underground'
FACEBOOK = 'facebook'
GOOGLE_MAPS = 'google_maps'
GOOGLE_ADDRESS = 'google_address'

FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

EXTERNAL_INTERFACES = {
    WEATHER_UNDERGROUND: {
        'url': 'http://api.wunderground.com/api/%s/conditions/astronomy/rawtide/q/%s/%s.json',
        'url_latlng': 'http://api.wunderground.com/api/%s/geolookup/conditions/astronomy/rawtide/q/%s,%s.json',
        'method': 'http://api.wunderground.com/api/%s/conditions/q/%s/%s.json',
        'apikey': 'd41784195576cec0',
    },

    FACEBOOK: {
        'app': '178799865530799',
        'secret': '502a5c37f483495170f0559afa4ad1ca',
        'url': 'https://graph.facebook.com/oauth/authorize'
    },

    GOOGLE_ADDRESS: {
        'url': 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false'
    }
}

MEMCACHE = {
    'server': ['127.0.0.1:11211']
}

# set up the external API stuff
WEATHER_API_KEY = 'd41784195576cec0' + '-'
WEATHER_API_URL = 'http://api.wunderground.com/api/%s/conditions/q/%s/%s.json'
#WEATHER_API_LAT_LNG_URL = 'http://api.wunderground.com/api/%s/conditions/q/%s/%s,%s.json'
WEATHER_API_LAT_LNG_URL = 'http://api.wunderground.com/api/%s/geolookup/conditions/astronomy/rawtide/q/%s,%s.json'

NOSQL_HOST = 'localhost'
NOSQL_PASSWORD = 'notset'
NOSQL_PORT = 27017
NOSQL_DB = 'scubamob'

#AWS_ACCESS_KEY_ID = 'AKIAJAKVVBLJNXEABZVQ'
#AWS_SECRET_ACCESS_KEY = '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'
AWS_ACCESS_KEY_ID = 'AKIAJDVN6XIBZ5I7TVSA'
AWS_SECRET_ACCESS_KEY = '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'

# Here is the bucket file pattern.  It goes in the following manner:
# account guid / album id / file name
GALLERY_BUCKET = 'scubamob.gallery.dev'

EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = 'no-reply@scubamob.com'
GOOGLE_API_KEY = 'AIzaSyD8CDOojSGLURvXDISrXKHZss1BkOA-Lss'

# this is a constant to be used to compute geodistance stuff
EARTH_RADIUS = 3159

# the following settings are for the mobile apps
MOBILE_HEADER_APP = 'scubaapp'
MOBILE_HEADER_DEVICES = {'smandroid': 'am', 'smios': 'io'}

# maxmind settings
#MAXMIND_URL = 'https://geoip.maxmind.com/geoip/v2.0/city_isp_org/%s'
MAXMIND_URL = 'https://geoip.maxmind.com/geoip/v2.0/city/%s'
MAXMIND_LICENSE = 'hVeqTCTxxU5H'
MAXMIND_USER = '75205'

# define the mongo collections
MONGO_DIVELOGS		= 'divelogs'

DEBUG_IP = '68.101.214.253'

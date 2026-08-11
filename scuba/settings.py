from pathlib import Path

import environ
import django.conf.global_settings as DEFAULT_SETTINGS


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment configuration
# Values from the OS environment take precedence over values in .env.
env = environ.Env(
    DEBUG=(bool, True),
    DJANGO_SECRET_KEY=(str, "dev-only-insecure-secret-key"),
    ALLOWED_HOSTS=(list, []),
    INTERNAL_IPS=(list, ["127.0.0.1", "10.0.2.2", "10.0.2.15"]),

    BASE_URL=(str, "http://localhost:8000"),
    SITE_URL=(str, "http://localhost:8000"),

    GOOGLE_API_KEY=(str, "google-api-key"),
    WEATHER_API_KEY=(str, "weather-api-key"),
    SETTINGS_SERVER=(str, "http://localhost:3003"),
    ALERTING_SERVER=(str, "http://localhost:3001"),
    ALERT_SERVER_ACTIVE=(bool, False),
    AWS_S3_BUCKET=(str, "scubamob-dev"),
    AWS_S3_BUCKET_PRIVATE=(str, "scubamob-private"),
    AWS_CLOUDFRONT=(str, 'https://NOTSET/'),
    AWS_CLOUDFRONT_DEPLOY=(str, 'https://NOTSET/'),

    CHAT_DYNAMODB_TABLE=(str, "scubamob-chat-dev"),
    CHAT_DYNAMODB_REGION=(str, "us-west-1"),
    CHAT_REDIS_URL=(str, "redis://localhost:6379/0"),
    CHAT_ATTACHMENT_BUCKET=(str, "scubamob-chat-attachments-dev"),
)

env.read_env(BASE_DIR / ".env")

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "static"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INTERNAL_IPS = env("INTERNAL_IPS")

BASE_URL = env("BASE_URL")
SITE_URL = env("SITE_URL")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# Cookie/transport hardening -- only enforced when DEBUG is off, so local
# development over plain http is unaffected.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 60 * 60 * 24 * 30  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'compressor',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    'scuba.accounts',
    'scuba.aws',
    'scuba.cache',
    'scuba.chat',
    'scuba.content',
    'scuba.divegroups',
    'scuba.diveshops',
    'scuba.divesites',
    'scuba.entities',
    'scuba.environ',
    'scuba.equipment',
    'scuba.galleries',
    'scuba.home',
    'scuba.logbooks',
    'scuba.maps',
    'scuba.robots',
    'scuba.search',
    'scuba.security',
    'scuba.sitesettings',
    'django.contrib.admindocs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scuba.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
             BASE_DIR / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'scuba.libs.context_processors.scuba.Scuba',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = DEFAULT_SETTINGS.AUTHENTICATION_BACKENDS + [
    'scuba.libs.authentication.usernameauthentication.UsernameAuthentication',
]

WSGI_APPLICATION = 'scuba.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
    )
}

AUTH_USER_MODEL = 'accounts.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'NON_FIELD_ERRORS_KEY': 'errors',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/min',
        'user': '2000/min',
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/home'
LOGIN_URL = '/login'


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_TZ = False
TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + [
    'compressor.finders.CompressorFinder',]

STATICFILES_DIRS = [
    BASE_DIR / "node_modules",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_FROM = 'no-reply@scubamob.com'
EMAIL_BCC = 'no-reply@scubamob.com'

PRODUCTION_GALLERY_URL = '//s3-us-west-1.amazonaws.com/scubamob.gallery.dev/'

FACEBOOK = 'facebook'
GOOGLE_MAPS = 'google_maps'
GOOGLE_ADDRESS = 'google_address'

FACEBOOK_APP = ''
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

# Here is the bucket file pattern.  It goes in the following manner:
# account guid / album id / file name
GALLERY_BUCKET = 'scubamob.gallery.dev'

EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = 'no-reply@scubamob.com'
GOOGLE_API_KEY = env("GOOGLE_API_KEY")
WEATHER_API_KEY = env("WEATHER_API_KEY")
SETTINGS_SERVER = env("SETTINGS_SERVER")
ALERTING_SERVER = env("ALERTING_SERVER")
ALERT_SERVER_ACTIVE = env.bool("ALERT_SERVER_ACTIVE")



CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# start AWS stuff
PROFILE_BLANK_URL = 'images/profiles/profile-blank.png'
BANNER_BLANK_URL = 'images/divesite-blank.png'
AWS_S3_BUCKET = env("AWS_S3_BUCKET") 
AWS_S3_BUCKET_PRIVATE = env("AWS_S3_BUCKET_PRIVATE")
AWS_S3_BUCKET_PRIVATE_REGION = 'us-east-1'
AWS_PROFILE = 'default'
AWS_EMAIL_STORAGE_ROOT = 'emailsent/skmradio'
AWS_CLOUDFRONT = env("AWS_CLOUDFRONT")
AWS_CLOUDFRONT_DEPLOY = env('AWS_CLOUDFRONT_DEPLOY')

CHAT_DYNAMODB_TABLE = env("CHAT_DYNAMODB_TABLE")
CHAT_DYNAMODB_REGION = env("CHAT_DYNAMODB_REGION")
CHAT_REDIS_URL = env("CHAT_REDIS_URL")
CHAT_ATTACHMENT_BUCKET = env("CHAT_ATTACHMENT_BUCKET")

FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.TemporaryFileUploadHandler']

SOCKET_SERVER = 'location:3001'
SOCKET_SERVER_ACTIVE = False

# Social Media
SOCIAL_MEDIA = {
    'FACEBOOK': 'https://www.facebook.com/scubamob/',
    'INSTAGRAM': 'https://www.instagram.com/scubamob/',
    'TWITTER': 'https://www.instagram.com/scubamob/'
}

SITE_ID = 1
SITE_NAME = 'ScubaMob'

VIDEO_TYPES = ['mp4']
IMAGE_TYPES = ['png', 'jpg', 'gif', 'jpeg']
VALID_CONTENT_TYPES = ['image/png', 'image/jpg', 'image/jpeg', 'video/mp4']

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

SITE_TITLE = 'ScubaMob'
TITLE_HTML = 'ScubaMob&reg;'
IS_PRODUCTION = env.bool('IS_PRODUCTION', default=False)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'settings': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
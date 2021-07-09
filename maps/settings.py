"""
Django settings for maps project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", 'django-insecure-tr#83t$_--71h1yzg^@w6n^w292lb#$1p2256)5k2-!^f^x9^d')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False)

ALLOWED_HOSTS = ['hospitals.trebuchet.one', 'needmedi.com', '127.0.0.1', '13.233.106.146']

if not DEBUG:
    DEPLOYMENT_URL = 'https://needmedi.com'

else:
    DEPLOYMENT_URL = 'http://127.0.0.1:8000'
    # DEPLOYMENT_URL = 'https://needmedi.com'

# Application definition

INSTALLED_APPS = [

    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'oauth2_provider',
    'social_django',
    'rest_framework',
    'rest_framework_social_oauth2',
    'django_filters',
    'oidc_provider',
    'rest_framework_swagger',
    'drf_yasg',
    'admin_honeypot',
    "log_viewer",
    # custom
    'home',
    'v2'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'maps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'maps.wsgi.application'

OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    "OIDC_RSA_PRIVATE_KEY": os.environ.get("OIDC_RSA_PRIVATE_KEY"),
    # this is the list of available scopes
    'SCOPES': {"openid": "See Profile",
               'read': 'Read Patient Data',
               'write': 'Add Patient Data',
               'groups': 'Add Invites'},
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore'
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30000/day',
        'user': '20000/day',
        'user_sec': '2/second',
        'user_min': '30/minute',
        'user_hour': '200/hour',
        'user_day': '2000/day',
    },
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

AUTHENTICATION_BACKENDS = (
    # Google OAuth2
    'social_core.backends.google.GoogleOAuth2',
    # django-rest-framework-social-oauth2
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    # Django
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',

)

# Default Client
DEFAULT_CLIENT = os.environ.get('DEFAULT_CLIENT')

# Google configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_SECRET')

# Define SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE to get extra permissions from Google.
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
LOGIN_URL = '/login/'

SWAGGER_SETTINGS = {
    'JSON_EDITOR': True
}

LOG_VIEWER_FILES = ['v2.log', 'home.log', 'default.log']
LOG_VIEWER_FILES_PATTERN = '*'
LOG_VIEWER_FILES_DIR = os.path.join(BASE_DIR, 'logs')
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_PAGE_LENGTH = 25  # total log lines per-page
LOG_VIEWER_PATTERNS = [']OFNI[', ']GUBED[', ']GNINRAW[', ']RORRE[', ']LACITIRC[']

# Optionally you can set the next variables in order to customize the admin:

LOG_VIEWER_FILE_LIST_TITLE = "Custom title"
LOG_VIEWER_FILE_LIST_STYLES = "/static/css/logs.css"
LOGGING_ROOT = os.path.join(BASE_DIR, 'logs')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'v2': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'v2.log'),
            'maxBytes': 1024 * 1024 * 15,  # 5MB
            'backupCount': 0,
            'formatter': 'standard',
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'default.log'),
            'maxBytes': 1024 * 1024 * 15,  # 5MB
            'backupCount': 0,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'request.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },

    },
    'formatters': {
        'standard': {
            'format': "[%(levelname)s] [%(asctime)s] [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'default'],
            'level': 'INFO',
            'propagate': True,
        },
        'v2': {
            'handlers': ['console', 'v2'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

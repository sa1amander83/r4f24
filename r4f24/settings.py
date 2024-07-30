"""
Django settings for r4f24 project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from shutil import which

from corsheaders.defaults import default_headers
from flower.api import tasks

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f=p0evvriyhde@nmw9ltz13-*@tr@j9cqs!f9cqduyq$odg@l1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:9000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
INTERNAL_IPS = [
    "127.0.0.1",
]
# Application definition

INSTALLED_APPS = [
    # 'compressor',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'fontawesomefree',
    'core',
    'profiles',
    'authorize',
    'groups',
    'django_cleanup',
    
    "debug_toolbar",


]

# from django.core.files.storage import get_storage_class

# from django_hashedfilenamestorage.storage import HashedFilenameMetaStorage

# HashedFilenameMyStorage = HashedFilenameMetaStorage(
#     storage_class=get_storage_class('core.MyStorage'),
# )


# DEFAULT_FILE_STORAGE = 'django_hashedfilenamestorage.storage.HashedFilenameFileSystemStorage'

CORS_ORIGIN_ALLOW_ALL = True





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",

    # "django.middleware.cache.UpdateCacheMiddleware",
    # "django.middleware.common.CommonMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",
    # "django_browser_reload.middleware.BrowserReloadMiddleware",
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_DIRS = []

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# COMPRESS_ROOT = BASE_DIR / 'static'
#
# COMPRESS_ENABLED = True
# STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',)

ROOT_URLCONF = 'r4f24.urls'
# DRAMATIQ_BROKER = {
#     "BROKER": "dramatiq.brokers.redis.RedisBroker",
#     "OPTIONS": {
#         "url": "redis://localhost:6379",
#     },
#     "MIDDLEWARE": [
#         "dramatiq.middleware.Prometheus",
#         "dramatiq.middleware.AgeLimit",
#         "dramatiq.middleware.TimeLimit",
#         "dramatiq.middleware.Callbacks",
#         "dramatiq.middleware.Retries",
#         "django_dramatiq.middleware.DbConnectionsMiddleware",
#         "django_dramatiq.middleware.AdminMiddleware",
#     ]
# }

# Defines which database should be used to persist Task objects when the
# AdminMiddleware is enabled.  The default value is "default".
# DRAMATIQ_TASKS_DATABASE = "default"
# from dramatiq.brokers.rabbitmq import RabbitmqBroker
#
#
# rabbitmq_broker = RabbitmqBroker(host="rabbitmq")
# dramatiq.set_broker(rabbitmq_broker)


# DRAMATIQ_RESULT_BACKEND = {
#     "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
#     "BACKEND_OPTIONS": {
#         "url": "redis://localhost:6379",
#     },
#     "MIDDLEWARE_OPTIONS": {
#         "result_ttl": 1000 * 60 * 10
#     }
# }


NPM_BIN_PATH = which('npm')
CSRF_COOKIE_NAME = "csrftoken"
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1']
CORS_ALLOW_HEADERS = list(default_headers) + [
    'xsrfheadername',
    'xsrfcookiename',
    'content-type',
    'x-csrftoken',
    'X-CSRFTOKEN',
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True

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
            ],
        },
    },
]

WSGI_APPLICATION = 'r4f24.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'HOST': 'localhost',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PORT': '5432',
        'PASSWORD': '123'}
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    # 'compressor.finders.CompressorFinder',
)
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'}
    },
    # 'loggers': {
    #     'django.db.backends': {
    #         'handlers': ['console'],
    #         'level': 'DEBUG'
    #     }
    # }
}
#
# CELERY_BROKER_URL = 'redis://redis:6379'
# CELERY_RESULT_BACKEND = 'redis://redis:6379'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
# CELERY_RESULT_EXTENDED = True
# CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Here
MEDIA_URL = '/media/'

# LOGIN_URL = "/login/"
#
# LOGIN_REDIRECT_URL = "/profile/"

# The number of seconds a password reset link is valid for (default: 3 days).
PASSWORD_RESET_TIMEOUT = 60 * 60 * 60 * 60

# django_redis
# https://github.com/jazzband/django-redis


AUTH_USER_MODEL = 'core.user'
# CACHES = {
#     "default": {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         "LOCATION": "redis://127.0.0.1:6379/",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#
#         }
#     }
# }
#
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR/ 'cache',
        "TIMEOUT": 60,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379",
#         "KEY_PREFIX": "r4f",
#         "TIMEOUT": 60 * 15,
#     }
# }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

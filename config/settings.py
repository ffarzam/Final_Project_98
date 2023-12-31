"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from django.utils.translation import gettext_lazy as _

from celery.schedules import crontab
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

LANGUAGES = [
    ("fa", _("Persian")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]
# CSRF_TRUSTED_ORIGINS = ["*"]
# ALLOWED_HOSTS = ["localhost"]
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'feeder',
    'interactions',
    'pages',
    'drf_spectacular',
    'django_celery_beat',
    'elasticsearch_dsl',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'rosetta',
    'minio_storage',

]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.custom_middleware.ElasticAPILoggerMiddleware'
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('NAME'),
        'HOST': os.environ.get('HOST'),
        'PORT': os.environ.get('PORT'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASSWORD')
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
MEDIA_URL = "/media/"
# STATIC_URL = 'static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATIC_ROOT = './staticfiles/'
# STATICFILES_DIRS = [
#     BASE_DIR / "staticfiles",
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.authentication.AuthBackend',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

PASSWORD_RESET_TIMEOUT = 300  # 5 minutes

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'reset_password': '2/300seconds',
        'set_password': '2/min',
        'verify_account': '2/300seconds',

    },

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'RSS Feed Aggregator API',
    'VERSION': '1.0.0',
}
ACCESS_TOKEN_TTL = 60 * 60 * 24 * 1  # 1 Day
REFRESH_TOKEN_TTL = 60 * 60 * 24 * 14  # 14 Day
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DEFAULT_TTL = 60 * 60 * 24 * 14  # 14 Days
REDIS_AUTH_TTL = 60 * 60 * 24 * 14  # 14 Day
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'TIMEOUT': REDIS_DEFAULT_TTL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },

    'auth': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/2',
        'TIMEOUT': REDIS_AUTH_TTL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },

    'celery_backends': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/3',

        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },

}

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')

CELERY_BROKER_URL = f'amqp://{RABBITMQ_HOST}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}/3'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_WORKER_CONCURRENCY = 5
CELERY_PREFETCH_MULTIPLIER = 1

ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST")
ELASTICSEARCH_PORT = os.environ.get("ELASTICSEARCH_PORT")

CELERY_BEAT_SCHEDULE = {
    'update_rss': {
        'task': 'feeder.tasks.update_all_rss',
        'schedule': crontab(hour=3, minute=30),

    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    'handlers': {
        'elasticsearch_handler': {
            'level': 'INFO',
            'class': 'config.elastic_log_handler.ElasticsearchHandler',
            'host': ELASTICSEARCH_HOST,
            'port': ELASTICSEARCH_PORT,
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    "loggers": {
        "elastic_logger": {
            "handlers": ["elasticsearch_handler"],
            "level": "INFO",
            'propagate': False
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            'propagate': False
        },

    },
}

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}

QUEUE_NAME_LIST = ["login", "register", "activate", "rss_feed_update", "refresh", "logout", "logout_all",
                   "selected_logout"]
AUTH_ALLOWED_NOTIFICATION = ["login", "register"]

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = 'minio:9000'
MINIO_EXTERNAL_STORAGE_ENDPOINT = "http://127.0.0.1:9000"

MINIO_STORAGE_ACCESS_KEY = os.environ.get("MINIO_ROOT_USER")
MINIO_STORAGE_SECRET_KEY = os.environ.get("MINIO_ROOT_PASSWORD")
MINIO_STORAGE_USE_HTTPS = False

MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = 'Recycle Bin'
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = '%c/'

MINIO_STORAGE_MEDIA_BUCKET_NAME = 'local-media'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True

MINIO_STORAGE_STATIC_BUCKET_NAME = 'local-static'
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

MINIO_STORAGE_STATIC_URL = f'{MINIO_EXTERNAL_STORAGE_ENDPOINT}/{MINIO_STORAGE_STATIC_BUCKET_NAME}'
MINIO_STORAGE_MEDIA_URL = f'{MINIO_EXTERNAL_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}'

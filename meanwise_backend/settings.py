"""
Django settings for meanwise_backend project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import logging
import datetime
from datetime import timedelta
from elasticsearch_dsl.connections import connections

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_URL = 'https://meanwise.com'

ADMINS = ()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_ks(exh8ftmi!f_vwma6od!#^$yngksnep2-n(5e6^qql%qcxx'

# Variables from Environment
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DATABASE = os.environ.get('DATABASE')
DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'meanwise')
DB_USER = os.environ.get('DB_USER', 'meanwise')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'meanwise1!')
SEARCH_ENGINE = os.environ.get('SEARCH_ENGINE', 'elasticsearch')
MEDIA_URL = os.environ.get('MEDIA_URL', 'http://localhost:8001/media/')
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
BASE_URI = os.environ.get('BASE_URI', 'http://localhost:8000/api/v4/')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
SENDGRID_NEW_USER_LIST_ID = os.environ.get('SENDGRID_NEW_USER_LIST_ID', '2016754')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'apikey')
EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD', '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')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS', True))
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = 'no-reply@meanwise.com'

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis:6379')

ELASTICSEARCH_USERNAME = os.environ.get('ELASTICSEARCH_USERNAME', None)
ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD', None)
HAYSTACK_ES_URL = os.environ.get('HAYSTACK_ES_URL', 'http://elasticsearch:9200/')
HAYSTACK_ES_INDEX_NAME = os.environ.get('HAYSTACK_ES_INDEX_NAME', 'meanwise_prod')

ELK_LOGSTASH_HOST = os.environ.get('ELK_LOGSTASH_HOST', None)
ELK_LOGSTASH_PORT = os.environ.get('ELK_LOGSTASH_PORT', None)

FILE_UPLOAD_PERMISSIONS = 0o644

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*', ]


# Application definition

INSTALLED_APPS = [
    'appversion',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'raven.contrib.django.raven_compat',
    'haystack',
    'restless',
    'rest_framework',
    'corsheaders',
    'storages',
    'health_check',
    #'common',
    #'geography',
    'mnotifications',
    'rest_framework.authtoken',

    # payment
    'djstripe',

    # elastic search
    'taggit',
    'taggit_serializer',

    # api v4
    'api_v4',
    'custom_auth',
    'userprofile.apps.UserprofileConfig',
    'post.apps.PostConfig',
    'discussions.apps.DiscussionsConfig',
    'boost.apps.BoostConfig',
    'brands.apps.BrandsConfig',
    'credits.apps.CreditsConfig',
    'college.apps.CollegeConfig',
    'follow.apps.FollowConfig',
    'topics.apps.TopicsConfig',
    'django_crontab',
    'scarface',
    'analytics',
]

if DEBUG:
    INSTALLED_APPS.append('silk')

SITE_ID = 1
REST_USE_JWT = True
ACCOUNT_ACTIVATION_DAYS = 1

MIDDLEWARE_CLASSES = [
    'log_request_id.middleware.RequestIDMiddleware',
    'meanwise_backend.middleware.ExtraRequestInfoMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Disabling CSRF by default
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'geography.middlewares.AddIPMiddleware',
]

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    MIDDLEWARE_CLASSES = ['silk.middleware.SilkyMiddleware', ] + MIDDLEWARE_CLASSES
else:
    CORS_ORIGIN_WHITELIST = ('meanwise.com', 'www.meanwise.com',)

DEVSERVER_AUTO_PROFILE = True

# setting for S3 storage
#DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE', 'django_s3_storage.storage.S3Storage')
DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE', 'storages.backends.s3boto3.S3Boto3Storage')
#THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-west-2')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'AKIAJW5PLC2EZMSQ4ZQQ')
AWS_ACCESS_KEY = AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = os.environ.get(
    'AWS_SECRET_ACCESS_KEY', 'aRR+qkRx7tsHzGQA8j1WBRaSmEnsMs8+PPr3N1f0')

# The name of the bucket to store files in.
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'mw-uploads-dev-1')
AWS_QUERYSTRING_AUTH = os.environ.get('AWS_QUERYSTRING_AUTH', False)
AWS_S3_FILE_OVERWRITE = os.environ.get('AWS_S3_FILE_OVERWRITE', False)
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', None)

#AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
#AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', "mw-uploads")
#AWS_S3_BUCKET_AUTH = False
#AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365
#AWS_S3_PUBLIC_URL = os.environ.get('AWS_S3_PUBLIC_URL', 'dtl635379s21p.cloudfront.net')

ROOT_URLCONF = 'meanwise_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'meanwise_backend.wsgi.application'

# stripe-settings
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_VW8VZ6dCNcurnmNhIsaC4F70")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_AJXKW5UHiXElOEBzMTJOVMKm")

PAYMENTS_PLANS = {
    "monthly": {
        "stripe_plan_id": "pro-monthly",
        "name": "Web App Pro ($25/month)",
        "description": "The monthly subscription plan to WebApp",
        "price": 25,
        "currency": "usd",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "pro-yearly",
        "name": "Web App Pro ($199/year)",
        "description": "The annual subscription plan to WebApp",
        "price": 199,
        "currency": "usd",
        "interval": "year"
    },
    "monthly-trial": {
        "stripe_plan_id": "pro-monthly-trial",
        "name": "Web App Pro ($25/month with 30 days free)",
        "description": "The monthly subscription plan to WebApp",
        "price": 25,
        "currency": "usd",
        "interval": "month",
        "trial_period_days": 30
    },
}

SEND_EMAIL_RECEIPTS = False

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}
# ACCOUNT_AUTHENTICATION_METHOD = 'username'

if DATABASE:
    DATABASES['default'] = DATABASES[DATABASE]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    #'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d  %(pathname)s %(funcName)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'django.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'meanwise_backend': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['console']
        },
        'celery': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
    },
}

if ELK_LOGSTASH_HOST:
    LOGGING['filters']['add_gelf_data'] = {
        '()': 'meanwise_backend.filters.GelfFilter'
    }
    LOGGING['handlers']['graypy'] = {
        'level': 'INFO',
        'class': 'graypy.GELFHandler',
        'host': ELK_LOGSTASH_HOST,
        'port': int(ELK_LOGSTASH_PORT),
        #'formatter': 'simple',
        'filters': ['request_id', 'add_gelf_data']
    }
    LOGGING['loggers']['django']['handlers'].append('graypy')
    LOGGING['loggers']['meanwise_backend']['handlers'].append('graypy')

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

# got MEDIA_URL from env at the beginning
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#AUTH_USER_MODEL = 'allauth.User'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

INVITE_CODE_EXPIRY = 7
IS_INVITE_ONLY_REGISTRATION_ENABLED = True

# JWT settings
JWT_EXPIRATION_DELTA = datetime.timedelta(days=7)
JWT_SECRET_KEY = SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_VERIFY = True
JWT_VERIFY_EXPIRATION = True
JWT_LEEWAY = 0
JWT_AUTH_HEADER_PREFIX = 'Bearer'

# Django Rest Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'EXCEPTION_HANDLER': 'meanwise_backend.utils.custom_exception_handler'
}

# CORS White listing
CORS_ORIGIN_WHITELIST = (
    'meanwise.com',
    'client.meanwise.com'
)
CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ORIGIN_WHITELIST += ('local.meanwise.com', 'local.meanwise.com:3000')


THUMBNAIL_ALIASES = {
    'account_profile.ProfileImage.image': {
        'thumb': {
            'size': (48, 48),
            'crop': True
        },
        'thumb@2x': {
            'size': (96, 96),
            'crop': True
        },
        'default': {
            'size': (128, 128),
            'crop': True
        },
        'default@2x': {
            'size': (256, 256),
            'crop': True
        },
    },
    'interests.Interest.cover_photo': {
        'default': {
            'size': (255, 140),
            'crop': True
        },
        'default@2x': {
            'size': (510, 280),
            'crop': True
        }
    }
}

THUMBNAIL_NAMER = 'easy_thumbnails.namers.alias'

hs_elasticsearch_settings = {
    'ENGINE': 'meanwise_backend.search.MeanwiseElasticSearchEngine',
    #'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
    'URL': HAYSTACK_ES_URL,
    'INDEX_NAME': HAYSTACK_ES_INDEX_NAME,
    'KWARGS': {}
}
if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    hs_elasticsearch_settings['KWARGS']['http_auth'] = (
        ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)

# Haystack Settings
HS_CONNECTIONS = {
    'elasticsearch': hs_elasticsearch_settings,
    'solr': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/core1',
    },
    'whoosh': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/whoosh/whoosh_index',
    },
}
HAYSTACK_CONNECTIONS = {}

HAYSTACK_CONNECTIONS['default'] = HS_CONNECTIONS[SEARCH_ENGINE]
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# django-elasticsearch-dsl
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': HAYSTACK_ES_URL
    }
}

# elasticsearch-dsl
connections.create_connection(hosts=[HAYSTACK_ES_URL])

# Reset password url
RESET_PASSWORD_URL = SITE_URL + '/reset_password/'
PASSWORD_RESET_EXPIRY_DAYS = 7

# Cache Settings
# CACHES = {
#    'default': {
#        'BACKEND': 'django_redis.cache.RedisCache',
#        'LOCATION': 'redis://' + REDIS_HOST,
#        'OPTIONS': {
#            "CLIENT_CLASS": "django_redis.client.DefaultClient",
#            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
#            "SERIALIZER": "django_redis.serializers.json.JSONSerializer"
#        }
#    }
#}
#CACHE_KEY_PREFIX = 'cc'
# CACHE_TIMEOUT = 1  # in hours

# Google API Key for Places Auto complete
GOOGLE_LOCATION_API_KEY = 'AIzaSyBPU3h4lDlKHZW17pci_bUZ5LVgimdlTYk'

# GeoIP Settings
GEOIP_PATH = os.path.join(BASE_DIR, 'geodata')

# Profile settings
PROFILE_PHOTO_STUB = SITE_URL + '/client/images/profilePictureStub.png'
COVER_PHOTO_STUB = SITE_URL + '/client/images/coverPictureStub.jpg'

# Celery Settings

CELERY_BROKER_URL = 'redis://%s/0' % REDIS_HOST
#CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#CELERYBEAT_SCHEDULE = {
#    'update-search-index-every-3hours': {
#        'task': 'search.tasks.update_search_index',
#        'schedule': timedelta(hours=3),
#        'kwargs': {'age': 3}
#    },
#}
#CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]

# Raven/Sentry Config
# if not DEBUG:
#    RAVEN_CONFIG = {
#        'dsn': 'https://e9630008d26c488d8b2955db4e97d3c8:a1b497ca107443858e4ed553ed42a8bc@app.getsentry.com/65196',
#    }

# Taggit Config
TAGGIT_CASE_INSENSITIVE = True

import mimetypes

# video
mimetypes.add_type("video/mp4", ".mp4", True)
mimetypes.add_type("video/3gpp", ".3gp", True)
mimetypes.add_type("video/quicktime", ".mov", True)
mimetypes.add_type("video/x-msvideo", ".avi", True)
mimetypes.add_type("video/x-ms-wmv", ".wmv", True)

# audio
mimetypes.add_type("audio/mpeg", ".mp3", True)
mimetypes.add_type("audio/x-wav", ".wav", True)
mimetypes.add_type("audio/x-ms-wma", ".wma", True)
mimetypes.add_type("audio/ogg", ".ogg", True)
mimetypes.add_type("audio/3gpp", ".3gp", True)
mimetypes.add_type("audio/aac", ".aac", True)
mimetypes.add_type("audio/aiff", ".aiff", True)

# pdf
mimetypes.add_type("application/pdf", ".pdf", True)

# cron  to store trending topics

CRONJOBS = [
    ('*/5 * * * *', 'post.cron.my_scheduled_job', '>> /tmp/cron.log 2>&1')
]

SCARFACE_REGION_NAME = "us-east-1"

SCARFACE_APNS_CERTIFICATE = "-----BEGIN CERTIFICATE-----\nMIIFjzCCBHegAwIBAgIIJ5Pnj/tAdUgwDQYJKoZIhvcNAQEFBQAwgZYxCzAJBgNV\nBAYTAlVTMRMwEQYDVQQKDApBcHBsZSBJbmMuMSwwKgYDVQQLDCNBcHBsZSBXb3Js\nZHdpZGUgRGV2ZWxvcGVyIFJlbGF0aW9uczFEMEIGA1UEAww7QXBwbGUgV29ybGR3\naWRlIERldmVsb3BlciBSZWxhdGlvbnMgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkw\nHhcNMTcwNDEzMDIxODI0WhcNMTgwNDEzMDIxODI0WjCBjjElMCMGCgmSJomT8ixk\nAQEMFWNvbS5tZWFud2lzZS5tZWFud2lzZTFDMEEGA1UEAww6QXBwbGUgRGV2ZWxv\ncG1lbnQgSU9TIFB1c2ggU2VydmljZXM6IGNvbS5tZWFud2lzZS5tZWFud2lzZTET\nMBEGA1UECwwKRlIyOTNGOTNGUTELMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQCivc2PP5bRKUCPBvdMWvQJ4K7neYKR8AosvLapx+tM\nEcg0d66zBGwUycoTJFKoo2df7IP8sD8KVGaVG946nfJJovABy34m8DI1W1xlo7Td\nWJpZbdeHqqQOBGdYYHiU+XQgmXN9bfa9ecOOHFSNqyl9qeWUTdVrKifKputZrUZH\nGA5397rBZOPIjCMUR3VZ/FIV1Vra39nifZmI/Ml10Wd9bfLgaXanJjE1NOFOK1NL\nqIt4EkB/sRaqb7qjhKXAD8WOFoOE0RbUl755ChG1d4GZs0Bh6oTBgHbncDIjhCpd\n9i/roTyXuA4TAYlB5L+jRfieaRjfLHHpXCjjOVzE1lIzAgMBAAGjggHlMIIB4TAd\nBgNVHQ4EFgQUDJXFS7ImQOp0A/AYmxukU70moPEwCQYDVR0TBAIwADAfBgNVHSME\nGDAWgBSIJxcJqbYYYIvs67r2R1nFUlSjtzCCAQ8GA1UdIASCAQYwggECMIH/Bgkq\nhkiG92NkBQEwgfEwgcMGCCsGAQUFBwICMIG2DIGzUmVsaWFuY2Ugb24gdGhpcyBj\nZXJ0aWZpY2F0ZSBieSBhbnkgcGFydHkgYXNzdW1lcyBhY2NlcHRhbmNlIG9mIHRo\nZSB0aGVuIGFwcGxpY2FibGUgc3RhbmRhcmQgdGVybXMgYW5kIGNvbmRpdGlvbnMg\nb2YgdXNlLCBjZXJ0aWZpY2F0ZSBwb2xpY3kgYW5kIGNlcnRpZmljYXRpb24gcHJh\nY3RpY2Ugc3RhdGVtZW50cy4wKQYIKwYBBQUHAgEWHWh0dHA6Ly93d3cuYXBwbGUu\nY29tL2FwcGxlY2EvME0GA1UdHwRGMEQwQqBAoD6GPGh0dHA6Ly9kZXZlbG9wZXIu\nYXBwbGUuY29tL2NlcnRpZmljYXRpb25hdXRob3JpdHkvd3dkcmNhLmNybDALBgNV\nHQ8EBAMCB4AwEwYDVR0lBAwwCgYIKwYBBQUHAwIwEAYKKoZIhvdjZAYDAQQCBQAw\nDQYJKoZIhvcNAQEFBQADggEBAKnynAkkDi3GX2eRgg2SsSbUnGSDEbwloCYRpKti\n8YM/rMK6Dk7ROQXQt5ML+lZ7mycAWhIfC9+XYqHCAifPYaTMWbBekktar3OboCoE\nXmfdIYT74VFL8wtC9mFX8s6Dq42fjYz/NOvDcMmdBcSzrSN/XiQvNIDfZNJQ35dE\nUQ8YJ6CIntiELAbO3umC9zQL9Jw5hwGD+1YA6lEYp7OqIQM+gH0aY0eT1g3pg6bs\ntkLrHRIuZI3kQk6DL0KYr7fgdxSnlbXgoVSxTfcLHA1ANUfyrUcd35sT84IRIu0S\nc40OTp4kQHzz+Puqrc4BKN3mXUdl4htcSdNZSd3z5wBNGPc=\n-----END CERTIFICATE-----"

SCARFACE_APNS_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCivc2PP5bRKUCP\nBvdMWvQJ4K7neYKR8AosvLapx+tMEcg0d66zBGwUycoTJFKoo2df7IP8sD8KVGaV\nG946nfJJovABy34m8DI1W1xlo7TdWJpZbdeHqqQOBGdYYHiU+XQgmXN9bfa9ecOO\nHFSNqyl9qeWUTdVrKifKputZrUZHGA5397rBZOPIjCMUR3VZ/FIV1Vra39nifZmI\n/Ml10Wd9bfLgaXanJjE1NOFOK1NLqIt4EkB/sRaqb7qjhKXAD8WOFoOE0RbUl755\nChG1d4GZs0Bh6oTBgHbncDIjhCpd9i/roTyXuA4TAYlB5L+jRfieaRjfLHHpXCjj\nOVzE1lIzAgMBAAECggEAa4M46gn4ePXn0JWpiqgL0Pq+ke2UdRU/o46InmGU8QxO\nV1s57spdHN6ywTKd6QsKoDSAfc9x1kEsBBYFGnR+PGeIZ6coEFFe2iEhSYR9WD3Q\nuoP2f4ocF6aRH7Gb989VCLRXt+WNvF9U8e2FbpJFNt+m6/L/q2yOHTNpCDWQ2CXe\nt+Ivj6pKEVmyazNCUjrO7M3M1t5I+MhVHHRyN2IjNTyxEHdnyjv+wku6lzhnQmCR\niUkn1mlSWH+2RgHnTAd0wmna5V+mzqeKNoC7e9duwE8ABCF7eT7uMqRohfNJG4Ts\njjvlbIYVqVkoZK6EdcyUyu3Sc2JIHT6ihC/sTJhcAQKBgQDMtHYjW7YcKCi+c2So\nzMEXzj5Ej+IWq9qGf1cDbk6gF7I8Hmatilk0XkFifHQZXfK1fJz2WVfF21rBv/Ar\nfc+USAF/Gp7r4OviQi8AsYPW90aQiL0gkGBhq0ent4atyLU4H6mmSyn20QaVQkW5\n3YOIEegxua5fKlzWXNByYIs5YwKBgQDLhXC1L8tjLqa6sI6FYGffyuuzf4aPzSUr\nCfgul5FhRoOrtLdWQLpkWOA25vvrDyduzhRQNQF4iDX/GVyVC0r5BTEJPoVZCMcm\nBHYck9QBh8JlkLOLAs1awpN49A5tK2cj9Vqd0U/T/0qBWb0NgSpAuqe0z0ebjA9o\nFAS5+Y1E8QKBgEsEYzrn9B/zc6L/xMa7apPfyB/2HqOyTP33Eps2RGgU5wNzHKvC\nRJiVZh7CfwWA0V5DEX6SFUFz9pmETm6Rx42OqcW7qrvEjI05NeJqK2eO7PQwuCaD\n4l5Il5TWA+wR3p93swM3DmTeCyyNweGwVPB7p3z5j/ZeHvGLx/Pyf3MDAoGBAKR3\nnII/MmxfSct6XGI6axb15A21U6enz459SvtT7t8eXc+HhdUFD9uB2wdjGFd3cpVf\nohjDDQI7iO8yrpeffaHJaTwgMyClMFJvrocfi2cFL7pl+kGvLQZYUVagW3wrY/ky\nEF2SxaD7IFlxjI56QAv5CwfZrfNsdxLTgpJLsbbxAoGAcqlKxHkvMYnSrpNHXzAY\nuyIO4q/KvOKpyw9iouqOviOBGB6bSjtenF5jIAJSevllx/lWjgtkSPPPBlMzRIBd\n9AJ6DSWBUdxnHmVOmt5ymovqtH+eEmPpTiWQdYPTY8WevzAs3k8ZdeZBDYQ0neWh\nsswadpMw0JvsPznL3IHDlJ8=\n-----END PRIVATE KEY-----"

AMAZON_SNS_APP_NAME = os.environ.get('AMAZON_SNS_APP_NAME', 'Meanwise_Dev')
AMAZON_SNS_TOPIC_NAME = os.environ.get('AMAZON_SNS_TOPIC_NAME', 'notification_dev')
AMAZON_SNS_PLATFORM_APNS = os.environ.get('AMAZON_SNS_PLATFORM_APNS', 'APNS_SANDBOX')

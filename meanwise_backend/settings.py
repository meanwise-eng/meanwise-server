"""
Django settings for meanwise_backend project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import datetime
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_URL = 'https://squelo.com'

ADMINS = ()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_ks(exh8ftmi!f_vwma6od!#^$yngksnep2-n(5e6^qql%qcxx'

# Variables from Environment
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DATABASE = os.environ.get('DATABASE')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'meanwise1!')
SEARCH_ENGINE = os.environ.get('SEARCH_ENGINE', 'whoosh')

EMAIL_HOST = os.environ.get('EMAIL_HOST', '127.0.0.1')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 1025)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1:6379')


# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*', ]


# Application definition

INSTALLED_APPS = [
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
    'easy_thumbnails',
    #'subscribe',
    #'api_v3',
    #'common',
    #'account_profile',
    #'hitcount',
    #'interests',
    #'geography',
    #'search',
    #'recommendation',
    #'jobs',
    #'pages',
    'djcelery',
    'stream',
    #'notifications',
    #'works',
    #'company',
    # auth
    #'allauth',
    #'allauth.account',
    #'allauth.socialaccount',
    #'allauth.socialaccount.providers.facebook',
    #'rest_auth',
    #'rest_auth.registration',
    'rest_framework.authtoken',

    # payment
    'djstripe',

    # elastic search
    'elasticutils.contrib.django',
    'taggit',

    # api v4
    'api_v4',
    'custom_auth',
    'userprofile',
]

SITE_ID = 1
REST_USE_JWT = True
ACCOUNT_ACTIVATION_DAYS = 1

MIDDLEWARE_CLASSES = [
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
        'NAME': 'meanwise',
        'USER': 'meanwise',
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
    },
    'loggers': {
        'meanwise_backend': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'

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
    'PAGE_SIZE': 20
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

# Haystack Settings
HS_CONNECTIONS = {
    'elasticsearch': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'meanwise_prod',
    },
    'solr': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/core1',
    },
    'whoosh': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}
HAYSTACK_CONNECTIONS = {}

if SEARCH_ENGINE:
    HAYSTACK_CONNECTIONS['default'] = HS_CONNECTIONS[SEARCH_ENGINE]
else:
    HAYSTACK_CONNECTIONS['default'] = HS_CONNECTIONS['whoosh']

# Email settings
EMAIL_HOST = EMAIL_HOST
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = int(EMAIL_PORT)
EMAIL_USE_TLS = False if EMAIL_USE_TLS == '0' else True
DEFAULT_FROM_EMAIL = 'hello@meanwise.com'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Reset password url
RESET_PASSWORD_URL = SITE_URL + '/reset_password/'
PASSWORD_RESET_EXPIRY_DAYS = 7

# Cache Settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://' + REDIS_HOST,
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer"
        }
    }
}
CACHE_KEY_PREFIX = 'cc'
CACHE_TIMEOUT = 1  # in hours

# Google API Key for Places Auto complete
GOOGLE_LOCATION_API_KEY = 'AIzaSyBPU3h4lDlKHZW17pci_bUZ5LVgimdlTYk'

# GeoIP Settings
GEOIP_PATH = os.path.join(BASE_DIR, 'geodata')

# Profile settings
PROFILE_PHOTO_STUB = SITE_URL + '/client/images/profilePictureStub.png'
COVER_PHOTO_STUB = SITE_URL + '/client/images/coverPictureStub.jpg'

# Celery Settings

BROKER_URL = 'redis://%s/0' % REDIS_HOST
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYBEAT_SCHEDULE = {
    'update-search-index-every-3hours': {
        'task': 'search.tasks.update_search_index',
        'schedule': timedelta(hours=3),
        'kwargs': {'age': 3}
    },
}
CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]

# Raven/Sentry Config
if not DEBUG:
    RAVEN_CONFIG = {
        'dsn': 'https://e9630008d26c488d8b2955db4e97d3c8:a1b497ca107443858e4ed553ed42a8bc@app.getsentry.com/65196',
    }

# ElasticSearch Config
ES_DISABLED = True
ES_URLS = ['http://127.0.0.1:9200/']
ES_INDEXES = {'default': 'main_index'}

# Taggit Config
TAGGIT_CASE_INSENSITIVE = True

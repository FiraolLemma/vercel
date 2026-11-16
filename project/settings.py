
# project/settings.py

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


# ==========================================================
# BASE CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR / '.env.local', override=True)

IS_VERCEL = os.getenv('VERCEL', '').strip().lower() in {
    '1', 'true', 'yes', 'on'
}

IS_RENDER = bool(os.getenv('RENDER_EXTERNAL_HOSTNAME'))

DEBUG = os.getenv(
    'DEBUG',
    'False' if IS_VERCEL else 'True'
).strip().lower() in {'1', 'true', 'yes', 'on'}

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ImproperlyConfigured(
        'SECRET_KEY is missing. Configure it in your environment.'
    )


# ==========================================================
# HOST CONFIGURATION
# ==========================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]

render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')

vercel_hostnames = [
    os.getenv('VERCEL_URL'),
    os.getenv('VERCEL_BRANCH_URL'),
]

for hostname in [render_hostname, *vercel_hostnames]:
    if hostname:
        hostname = hostname.removeprefix('https://').removeprefix('http://').rstrip('/')
        if hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(hostname)

if IS_VERCEL and '.vercel.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.vercel.app')


# ==========================================================
# CSRF CONFIGURATION
# ==========================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip('/')
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS', ''
    ).split(',')
    if origin.strip()
]

if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ])

for hostname in [render_hostname, *vercel_hostnames]:
    if hostname:
        hostname = hostname.removeprefix('https://').removeprefix('http://').rstrip('/')
        CSRF_TRUSTED_ORIGINS.append(f'https://{hostname}')

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))


# ==========================================================
# SECURITY SETTINGS
# ==========================================================

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_PROXY_SSL_HEADER = (
    ('HTTP_X_FORWARDED_PROTO', 'https')
    if IS_VERCEL or IS_RENDER
    else None
)

SECURE_SSL_REDIRECT = (
    os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
)

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# ==========================================================
# INTERNATIONALIZATION
# ==========================================================

LANGUAGES = [
    ('en', _('English')),
    ('am', _('Amharic')),
    ('om', _('Oromiffa')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax'

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Addis_Ababa'

USE_I18N = True
USE_TZ = True


# ==========================================================
# INSTALLED APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'daphne',
    'channels',
    'rest_framework',
    'corsheaders',

    # Main applications
    'base',
    'poultrys.apps.PoultrysConfig',
    'conversation',
    'users',
    'contact',
    'companies',
    'dairys.apps.DairysConfig',
    'admin_app',
    'cart',
    'virtual_users',

    # Crispy Forms
    'crispy_forms',
    'crispy_bootstrap5',
]


# ==========================================================
# CRISPY FORMS
# ==========================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'users.middleware.OnboardingMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==========================================================
# URL AND APPLICATION CONFIGURATION
# ==========================================================

ROOT_URLCONF = 'project.urls'

ASGI_APPLICATION = 'project.asgi.application'

WSGI_APPLICATION = 'project.wsgi.application'

DAPHNE_TIMEOUT = 50


# ==========================================================
# DATABASE CONFIGURATION - NEON POSTGRESQL
# ==========================================================

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=0 if IS_VERCEL else 600,
            ssl_require=not DEBUG,
        )
    }

elif IS_VERCEL:
    raise ImproperlyConfigured(
        'DATABASE_URL is required on Vercel. '
        'Configure your Neon PostgreSQL connection.'
    )

else:
    # Local development fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==========================================================
# REDIS AND DJANGO CHANNELS
# ==========================================================

REDIS_URL = os.getenv('REDIS_URL')

if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }

else:
    if IS_VERCEL:
        raise ImproperlyConfigured(
            'REDIS_URL is required on Vercel. '
            'Configure a Redis-compatible service.'
        )

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }


# ==========================================================
# USER AUTHENTICATION
# ==========================================================

AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'users.backends.UsernamePhoneBackend',
]

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'users:dashboard'

LOGOUT_REDIRECT_URL = 'base:index'


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        },
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================================
# CLOUDINARY CONFIGURATION
# ==========================================================

cloudinary_credentials = (
    os.getenv('CLOUDINARY_CLOUD_NAME'),
    os.getenv('CLOUDINARY_API_KEY'),
    os.getenv('CLOUDINARY_API_SECRET'),
)

if any(cloudinary_credentials) and not all(cloudinary_credentials):
    raise ImproperlyConfigured(
        'Configure all three Cloudinary variables: '
        'CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, '
        'CLOUDINARY_API_SECRET.'
    )

if IS_VERCEL and not all(cloudinary_credentials):
    raise ImproperlyConfigured(
        'Cloudinary credentials are required on Vercel '
        'for persistent media uploads.'
    )

if all(cloudinary_credentials):
    import cloudinary

    INSTALLED_APPS += [
        'cloudinary_storage',
        'cloudinary',
    ]

    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': cloudinary_credentials[0],
        'API_KEY': cloudinary_credentials[1],
        'API_SECRET': cloudinary_credentials[2],
    }

    cloudinary.config(
        cloud_name=cloudinary_credentials[0],
        api_key=cloudinary_credentials[1],
        api_secret=cloudinary_credentials[2],
        secure=True,
    )


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfile'

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

WHITENOISE_AUTOREFRESH = DEBUG


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================================
# FILE STORAGE
# ==========================================================

STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if all(cloudinary_credentials)
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },

    'staticfiles': {
        'BACKEND':
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

CORS_ALLOWED_ORIGINS = [
    origin.strip().rstrip('/')
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS', ''
    ).split(',')
    if origin.strip()
]


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        'BACKEND':
            'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_item_count',
            ],
        },
    },
]


# ==========================================================
# DEFAULT MODEL FIELD
# ==========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

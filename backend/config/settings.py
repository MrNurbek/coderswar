from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    # Local apps
    'apps.users',
    'apps.courses',
    'apps.gamification',
    'apps.social',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# # ── DATABASE ─────────────────────────────────────────────────
# _db_engine = config('DB_ENGINE', default='sqlite')
# if _db_engine == 'postgresql':
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': config('DB_NAME', default='coderswar'),
#             'USER': config('DB_USER', default='postgres'),
#             'PASSWORD': config('DB_PASSWORD', default='postgres'),
#             'HOST': config('DB_HOST', default='localhost'),
#             'PORT': config('DB_PORT', default='5432'),
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# ── CACHE / REDIS ─────────────────────────────────────────────
_use_redis = config('USE_REDIS', default=False, cast=bool)

if _use_redis:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [config('REDIS_URL', default='redis://localhost:6379/0')],
            },
        },
    }
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
    CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}

# ── AUTH ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── REST FRAMEWORK ────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

# ── CORS ──────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:8000,http://localhost:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ── EMAIL ─────────────────────────────────────────────────────
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')


# ── DEFAULT FROM EMAIL ───────────────────────────────────────
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='noreply@coderswar.uz')

# ── EXTERNAL APIS ─────────────────────────────────────────────
JUDGE0_URL = config('JUDGE0_URL', default='http://localhost:2358')
JUDGE0_API_KEY = config('JUDGE0_API_KEY', default='')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# ── STATIC / MEDIA ────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# frontend/static/ → /static/frontend/ (local dev + collectstatic uchun)
STATICFILES_DIRS = [
    ('frontend', FRONTEND_DIR / 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── PRODUCTION SECURITY ───────────────────────────────────
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER   = True
    SESSION_COOKIE_SECURE        = True
    CSRF_COOKIE_SECURE           = True
    X_FRAME_OPTIONS              = 'DENY'
    # Nginx HTTPS'ni handle qiladi — Django redirect kerak emas
    SECURE_SSL_REDIRECT          = False
    SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── LOGGING ───────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '[{levelname}] {asctime} {module}: {message}', 'style': '{'},
        'simple':  {'format': '[{levelname}] {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django':          {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'apps':            {'handlers': ['console'], 'level': 'INFO',    'propagate': False},
    },
}

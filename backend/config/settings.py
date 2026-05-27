from pathlib import Path
from datetime import timedelta

from decouple import config


# ── BASE DIRS ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'


# ── SECURITY ─────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        'ALLOWED_HOSTS',
        default='localhost,127.0.0.1,192.168.0.103'
    ).split(',')
    if host.strip()
]


# ── APPLICATIONS ─────────────────────────────────────────────
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
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


# ── MIDDLEWARE ───────────────────────────────────────────────
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


# ── URL / WSGI / ASGI ────────────────────────────────────────
ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ── CUSTOM USER ──────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'


# ── TEMPLATES ────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Agar HTML fayllarni Django orqali render qilsangiz,
        # frontend papkasi ham template sifatida ko‘rinadi.
        'DIRS': [
            FRONTEND_DIR,
        ],

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


# ── DATABASE ─────────────────────────────────────────────────
DB_ENGINE = config('DB_ENGINE', default='sqlite')

if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='coderswar'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ── CACHE / REDIS / CHANNELS ─────────────────────────────────
USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }


# ── PASSWORD VALIDATION ──────────────────────────────────────
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


# ── REST FRAMEWORK ───────────────────────────────────────────
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


# ── SIMPLE JWT ───────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}


# ── CORS ─────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default=(
            'http://localhost:3000,'
            'http://127.0.0.1:3000,'
            'http://localhost:5173,'
            'http://127.0.0.1:5173,'
            'http://localhost:5500,'
            'http://127.0.0.1:5500,'
            'http://localhost:8080,'
            'http://127.0.0.1:8080,'
            'http://localhost:8000,'
            'http://127.0.0.1:8000,'
            'http://192.168.0.103:8000,'
            'http://192.168.0.103:5173'
        )
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True


# ── CSRF ─────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CSRF_TRUSTED_ORIGINS',
        default=(
            'http://localhost:8000,'
            'http://127.0.0.1:8000,'
            'http://192.168.0.103:8000'
        )
    ).split(',')
    if origin.strip()
]


# ── EMAIL ────────────────────────────────────────────────────
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default=config('EMAIL_HOST_USER', default='noreply@coderswar.uz')
)


# ── EXTERNAL APIS ────────────────────────────────────────────
JUDGE0_URL = config('JUDGE0_URL', default='http://localhost:2358')
JUDGE0_API_KEY = config('JUDGE0_API_KEY', default='')

OPENAI_API_KEY = config('OPENAI_API_KEY', default='')


# ── STATIC / MEDIA ───────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Asosiy static papkalar:
#
# 1) backend/static/
# 2) frontend/static/
#
# Muhim:
# Bu yerda ('frontend', FRONTEND_DIR / 'static') ishlatilmaydi.
# Chunki u holda fayllar /static/frontend/... bo‘lib ketadi.
#
# Quyidagi sozlama bilan:
# frontend/static/images/rank-warden.png
#
# mana bunday ochiladi:
# http://127.0.0.1:8000/static/images/rank-warden.png

BACKEND_STATIC_DIR = BASE_DIR / 'static'
FRONTEND_STATIC_DIR = FRONTEND_DIR / 'static'

STATICFILES_DIRS = []

if BACKEND_STATIC_DIR.exists():
    STATICFILES_DIRS.append(BACKEND_STATIC_DIR)

if FRONTEND_STATIC_DIR.exists():
    STATICFILES_DIRS.append(FRONTEND_STATIC_DIR)


# Localda manifest storage kerak emas.
# Manifest storage collectstatic qilinmagan fayllarda xatolik chiqarishi mumkin.
# Shuning uchun DEBUG=True bo‘lganda oddiy StaticFilesStorage ishlatiladi.
STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.StaticFilesStorage'
    if DEBUG
    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ── INTERNATIONALIZATION ─────────────────────────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True


# ── DEFAULT PRIMARY KEY ──────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── PRODUCTION SECURITY ──────────────────────────────────────
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    X_FRAME_OPTIONS = 'DENY'

    # HTTPS odatda Nginx orqali boshqariladi.
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ── LOGGING ──────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
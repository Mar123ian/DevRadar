import os
import ssl
import urllib.parse
from pathlib import Path
import dj_database_url
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Зарежда локални променливи само при разработка (локално)
load_dotenv(BASE_DIR / ".dev.env")

# --- СИГУРНОСТ И ОСНОВНИ НАСТРОЙКИ ---
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key-for-dev")
DEBUG = os.environ.get("DEBUG", "False") == "True"
PRODUCTION = os.environ.get("PRODUCTION", "False") == "True"

# Coolify подава ALLOWED_HOSTS като стрингове с запетая
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Динамично извличане на CSRF Trusted Origins (за HTTPS в Coolify)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

if PRODUCTION:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    USE_X_FORWARDED_HOST = True

    # Cloudflare Turnstile ключове
    TURNSTILE_SITEKEY = os.environ.get("TURNSTILE_SITEKEY")
    TURNSTILE_SECRETKEY = os.environ.get("TURNSTILE_SECRETKEY")

    # (По избор) Изглед на виджета: 'auto', 'light', или 'dark'
    TURNSTILE_DEFAULT_CONFIG = {
        "theme": "auto",
    }

# --- ИНТЕРНАЦИОНАЛИЗАЦИЯ ---
LANGUAGE_CODE = 'bg'
LANGUAGES = [
    ('bg', _('Bulgarian')),
    ('en', _('English')),
]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- ПРИЛОЖЕНИЯ И МИДЪЛУЕР ---
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'storages',
    'rest_framework',
    'rest_framework.authtoken',
    'programmers.apps.ProgrammersConfig',
    'comments.apps.CommentsConfig',
    'services.apps.ServicesConfig',
    'categories.apps.CategoriesConfig',
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'services_api.apps.ServicesApiConfig',
    'chat.apps.ChatConfig',
    'channels',
    'moderation.apps.ModerationConfig',
    'djcelery_email',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "turnstile",
]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'middlewares.IsBannedMiddleware',
#     'django.middleware.locale.LocaleMiddleware',
#     'middlewares.ForceDefaultLanguageMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'allauth.account.middleware.AccountMiddleware',
#     'middlewares.BlockUnverifiedEmailMiddleware',
#     'middlewares.GlobalRatelimitMiddleware'
# ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # 👈 Зареждаме езика ВЕДНАГА след сесията
    'middlewares.ForceDefaultLanguageMiddleware',  # 👈 Настройва езика по подразбиране
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Кастъм проверки за потребителя (вече имат достъп до request.user И зареден език)
    'middlewares.IsBannedMiddleware',
    'middlewares.BlockUnverifiedEmailMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',

    # Ratelimit (ако разчита на request.user за user_or_ip)
    'middlewares.GlobalRatelimitMiddleware',
]

ROOT_URLCONF = 'devradar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'devradar.wsgi.application'
ASGI_APPLICATION = 'devradar.asgi.application'
AUTH_USER_MODEL = 'accounts.DevRadarUser'

# --- БАЗА ДАННИ ---
# В Coolify ползваш DATABASE_URL или отделни DB_* променливи
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "devradar"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# --- СТАТИЧНИ И МЕДИЙНИ ФАЙЛОВЕ ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

    # Спира грешките от типа "MissingFileError" за служебните CSS файлове на Django Admin
    WHITENOISE_MANIFEST_STRICT = False

    # --- CLOUDINARY CONFIGURATION ---
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
    }

# --- REDIS И CELERY ---
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# --- ИМЕЙЛ НАСТРОЙКИ ---
if PRODUCTION:
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))

    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'

    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'apikey')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'DevRadar <no-reply@devradar.digital>')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else:
    DEFAULT_FROM_EMAIL = 'devradar.no.reply@gmail.com'
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    CELERY_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- ALLAUTH & AUTHENTICATION ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
ACCOUNT_SET_PASSWORD_REDIRECT_URL = '/accounts/profile/'
ACCOUNT_CHANGE_PASSWORD_REDIRECT_URL = '/accounts/profile/'

ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_ADAPTER = 'devradar.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online', 'prompt': 'select_account'}
    }
}
ACCOUNT_ADAPTER = 'devradar.adapters.CustomAccountAdapter'
ACCOUNT_ALLOW_EMAIL_CHANGE = True
ACCOUNT_USERNAME_GENERATOR = "accounts.utils.generate_username_from_email"
# ACCOUNT_RATE_LIMITS = {"send_mail": "1/2m",}
# ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 60
ACCOUNT_RATE_LIMITS = {
    "confirm_email": "10/d/ip, 10/d/key",
    "reset_password": "10/d/ip, 10/d/key",
}
ACCOUNT_EMAIL_CONFIRMATION_HMAC = False
ACCOUNT_FORMS = {'signup': 'accounts.forms.DevRadarUserCreationForm'}
SOCIALACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSocialSignupForm',
}

# --- ЛОГОВЕ ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
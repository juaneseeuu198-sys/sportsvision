from pathlib import Path
import os
import sys

# Soporte para ejecutable PyInstaller
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Producción: SECRET_KEY desde variable de entorno
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-sportsvision-dev-key-change-in-production'
)

# Producción: DEBUG=False cuando se define la variable de entorno
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://*.up.railway.app,https://*.railway.app'
    ).split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # SportsVision apps
    'apps.users',
    'apps.routines',
    'apps.exercises',
    'apps.tools',
    'apps.progress',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sportsvision.middleware.SuspensionMiddleware',
]

ROOT_URLCONF = 'sportsvision.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'sportsvision.wsgi.application'

import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
else:
    # Sin DATABASE_URL: solo permitido en build-time (collectstatic).
    # En runtime el startCommand de railway.toml falla en 'migrate' si no hay URL.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

AUTHENTICATION_BACKENDS = [
    'apps.users.backends.EmailOrUsernameBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('es', _('Español')),
    ('en', _('English')),
    ('pt', _('Português')),
    ('fr', _('Français')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth redirects
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Configuración de Email ─────────────────────────────────────────────────────
# En desarrollo: muestra el email en consola
# En producción: configura las variables de entorno para Gmail u otro servidor

BREVO_API_KEY     = os.environ.get('BREVO_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# URL base para los enlaces en los correos
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8000')

# ── Proxy Railway (HTTPS externo, HTTP interno) ────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST    = True

# ── Cookies ────────────────────────────────────────────────────────────────────
# SameSite=Lax (default Django): válido en Chrome/WebView sin necesitar Secure.
# El CookieManager del WebView Android acepta estas cookies correctamente.
# SameSite=None + Secure=True: máxima compatibilidad con Safari iOS, Android WebView,
# y Chrome. SECURE_PROXY_SSL_HEADER garantiza que Django sepa que está en HTTPS.
CSRF_COOKIE_SAMESITE    = 'None'
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE      = True
SESSION_COOKIE_SECURE   = True


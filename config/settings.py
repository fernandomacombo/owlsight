import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# Segurança / Ambiente
# =========================
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-only-unsafe-secret-key"

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

# Em DEV pode ser "*", em PROD evita. No Railway põe ALLOWED_HOSTS com o teu domínio.
_raw_hosts = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]

# CSRF_TRUSTED_ORIGINS precisa do esquema (https://...)
_raw_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _raw_csrf.split(",") if o.strip()]


# =========================
# Apps
# =========================
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # terceiros (confere se estão no requirements!)
    "rest_framework",
    "storages",
    "axes",
    "csp",

    # apps do projeto
    "frontend",
    "books",
    "reading",
    "accounts",
]


# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise para servir static no Railway
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # CSP (anti XSS)
    "csp.middleware.CSPMiddleware",

    # Axes (anti brute-force) -> ideal no fim
    "axes.middleware.AxesMiddleware",
]


# =========================
# Auth backends
# =========================
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# =========================
# Database (Postgres no Railway / SQLite local)
# =========================
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=os.getenv("DB_SSL_REQUIRE", "True").lower() in ("1", "true", "yes", "on"),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =========================
# i18n / timezone
# =========================
LANGUAGE_CODE = "pt-pt"
TIME_ZONE = "Africa/Maputo"
USE_I18N = True
USE_TZ = True


# =========================
# DRF (base)
# =========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# =========================
# Static (WhiteNoise)
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}


# =========================
# Media / Storage (Backblaze B2 via S3)
# =========================
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "path")
AWS_QUERYSTRING_AUTH = os.getenv("AWS_QUERYSTRING_AUTH", "True").lower() in ("1", "true", "yes", "on")

AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

USE_B2 = all([
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_ENDPOINT_URL,
])

MEDIA_URL = "/media/"

if USE_B2:
    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}
else:
    MEDIA_ROOT = BASE_DIR / "media"


# =========================
# Upload limits
# =========================
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024


# =========================
# Segurança forte (produção)
# =========================
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Proxy header (Railway/Render/etc)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Só redireciona para https se estiver atrás de proxy que seta X_FORWARDED_PROTO
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("1", "true", "yes", "on")

    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# URLs de auth
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# =========================
# AXES (anti brute-force)
# =========================
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas
AXES_RESET_ON_SUCCESS = True

# Bloqueia por username + ip
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_USERNAME_FORM_FIELD = "username"
AXES_ENABLE_ACCESS_FAILURE_LOG = True


# =========================
# CSP (django-csp)
# =========================
# ✅ Formato novo (django-csp >= 4)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "connect-src": ("'self'",),
        "img-src": ("'self'", "data:", "blob:"),
        "font-src": ("'self'", "data:"),
        "script-src": ("'self'", "https://cdn.tailwindcss.com", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
    }
}

# ✅ Fallback (caso a tua versão do django-csp ainda seja antiga)
# Se estiveres no django-csp 4, isto é ignorado sem problema.
CSP_DEFAULT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:", "blob:")
CSP_FONT_SRC = ("'self'", "data:")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.tailwindcss.com", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")


# =========================
# Outros
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Logging
# =========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": True},
        "django.security": {"handlers": ["console"], "level": "ERROR", "propagate": True},
        "axes.watch_login": {"handlers": ["console"], "level": "WARNING", "propagate": True},
    },
}
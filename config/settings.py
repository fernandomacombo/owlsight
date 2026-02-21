import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# ✅ Extras de segurança (instala: pip install django-axes django-csp)
# Axes = bloqueio anti brute-force
# CSP  = Content-Security-Policy (anti XSS)

# Carrega .env local (no Railway, use Variables do painel)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# Segurança / Ambiente
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    # Apenas para DEV local (no Railway você DEVE definir SECRET_KEY)
    SECRET_KEY = "dev-only-unsafe-secret-key"

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]


# =========================
# Apps
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # terceiros
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

    # Axes (anti brute-force) -> deve ficar por último
    "axes.middleware.AxesMiddleware",
]


# =========================
# Auth backends
# =========================
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
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
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")  # assinatura
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

if USE_B2:
    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}
    MEDIA_URL = "/media/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"


# =========================
# Upload limits (ajuste conforme plano)
# =========================
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024      # 200MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024      # 200MB


# =========================
# Segurança forte (produção)
# =========================
# Cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Headers
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# HTTPS/HSTS apenas em produção
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 dias (depois aumente)
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
AXES_FAILURE_LIMIT = 5        # 5 falhas
AXES_COOLOFF_TIME = 1         # 1 hora bloqueado
AXES_RESET_ON_SUCCESS = True
# Bloqueia por combinação (username + ip)
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_USERNAME_FORM_FIELD = "username"
AXES_ENABLE_ACCESS_FAILURE_LOG = True


# =========================
# CSP (django-csp >= 4.0) — formato novo
# =========================
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "connect-src": ("'self'",),
        "img-src": ("'self'", "data:", "blob:"),
        "font-src": ("'self'", "data:"),
        # Tailwind CDN + inline (por causa do toggle password e tailwind CDN)
        "script-src": ("'self'", "https://cdn.tailwindcss.com", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
    }
}


# =========================
# Outros
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Logging (erros importantes)
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
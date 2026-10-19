import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set DJANGO_SECRET_KEY in the PythonAnywhere WSGI file / environment.
# NOTE: stored API keys are encrypted with a key derived from this, so don't change it
# after users have saved keys (they'd have to re-enter them).
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("DJANGO_CSRF_ORIGINS", "").split(",") if o]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "textbooks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "textbook_list"
LOGOUT_REDIRECT_URL = "login"

# Uploaded decks are only read into memory, never stored. Keep them small.
DATA_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024
MAX_PPTX_BYTES = 25 * 1024 * 1024

# AI settings
# "mistral" (default) or "anthropic"
AI_PROVIDER = os.environ.get("Lectern_AI_PROVIDER", "mistral")
_DEFAULT_MODELS = {"mistral": "mistral-small-latest", "anthropic": "claude-haiku-5-5"}
AI_MODEL = os.environ.get("Lectern_AI_MODEL", _DEFAULT_MODELS.get(AI_PROVIDER, ""))  # default for users who haven't chosen
_MODEL_CHOICES = {
    "mistral": [
        ("mistral-small-latest", "Mistral Small: cheapest, good for testing"),
        ("mistral-medium-latest", "Mistral Medium: balanced"),
        ("mistral-large-latest", "Mistral Large: most capable, most expensive"),
    ],
    "anthropic": [
        ("claude-haiku-5-5", "Haiku 5.5: cheapest, good for testing"),
        ("claude-sonnet-5-5", "Sonnet 5.5: balanced, good for real study notes"),
        ("claude-opus-5-5", "Opus 5.5: most capable, most expensive"),
    ],
}
AI_MODEL_CHOICES = _MODEL_CHOICES.get(AI_PROVIDER, [])
AI_MAX_TOKENS = 3000
# Long decks are split into several smaller requests (kinder to free-tier rate limits).
AI_SLIDES_PER_CHUNK = 5
AI_CHARS_PER_CHUNK = 6000      # also split when a chunk's slide text exceeds this
AI_PAUSE_SECONDS = 1.5         # pause between requests
AI_PROMPT = (
    "Write an explainer in the style of a biology textbook. "
    "You can utilise mermaid diagrams, as Obsidian supports them."
)

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

from core.settings import base

INSTALLED_APPS = base.INSTALLED_APPS
MIDDLEWARE = base.MIDDLEWARE
TEMPLATES = base.TEMPLATES

SECRET_KEY = "test-secret-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = base.ROOT_URLCONF
WSGI_APPLICATION = base.WSGI_APPLICATION
ASGI_APPLICATION = base.ASGI_APPLICATION
REST_FRAMEWORK = base.REST_FRAMEWORK

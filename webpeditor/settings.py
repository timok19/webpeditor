"""
Django settings for webpeditor project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
import cloudinary
from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv(key="SECRET_KEY", default=get_random_secret_key()))

# Default file storage
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media" / "uploaded_images"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "0").lower() in ["true", "t", "1"]

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "webpeditor.fly.dev"]

CSRF_TRUSTED_ORIGINS = [str(os.getenv("CSRF_TRUSTED_ORIGINS"))]

# Application definition
# In development mode. Delete this in production mode (add domains in white list)
INSTALLED_APPS = [
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "cloudinary",
    "compressor",
    "rest_framework",
    "corsheaders",
    "webpeditor_app.apps.WebpeditorAppConfig",
]

# Delete in production
# CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://webpeditor.fly.dev",
    "https://res.cloudinary.com",
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "webpeditor.urls"

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

WSGI_APPLICATION = "webpeditor.wsgi.application"

ONE_MEGABYTE = 1_000_000

MAX_IMAGE_FILE_SIZE = 6_000_000

MAX_SUM_SIZE_OF_IMAGE_FILES = 50_000_000

DATA_UPLOAD_MAX_NUMBER_FILES = 15

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

FILE_UPLOAD_MAX_MEMORY_SIZE = 10_485_760 * 4

DATA_UPLOAD_MAX_MEMORY_SIZE = 52_428_800 * 4

VALID_IMAGE_FORMATS = ["WEBP", "JPEG", "JPG", "PNG", "JFIF", "ICO", "BMP", "GIF", "TIFF"]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        # "CLIENT": {
        #     # Add local env variables to store host string
        #     "host": f'mongodb+srv://{os.getenv("DATABASE_USER")}:'
        #     f'{os.getenv("DATABASE_PASSWORD")}'
        #     f'{os.getenv("HOST_LINK")}/?retryWrites=true&w=majority',
        #     "name": str(os.getenv("DATABASE_NAME")),
        #     "authMechanism": str(os.getenv("AUTH_MECHANISM")),  # For atlas cloud db
        # },
    }
}

# Path for future migrations
MIGRATION_MODULES = {"webpeditor_app": "webpeditor_app.models.database.migrations"}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Session handling

SESSION_SAVE_EVERY_REQUEST = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_SAMESITE = "Strict"

CSRF_COOKIE_SAMESITE = "Strict"

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

# PROD ONLY
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_FINDERS = ["compressor.finders.CompressorFinder"]

# Cloudinary's storage config
cloudinary.config(
    cloud_name=str(os.getenv("CLOUDINARY_CLOUD_NAME")),
    api_key=str(os.getenv("CLOUDINARY_API_KEY")),
    api_secret=str(os.getenv("CLOUDINARY_API_SECRET")),
    secure=True,
)

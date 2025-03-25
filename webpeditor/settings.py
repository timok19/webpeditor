"""
Django settings for webpeditor project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import django_stubs_ext

from datetime import timedelta

from django.core.management.utils import get_random_secret_key
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from webpeditor_app.apps import WebpeditorAppConfig

django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent

ENV_FILE_PATH: Path = BASE_DIR / ".env"

# Load .env file
if ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True, verbose=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = os.getenv("SECRET_KEY") or get_random_secret_key()

WEBPEDITOR_API_KEY: str = str(os.getenv("WEBPEDITOR_API_KEY"))

WEBPEDITOR_SALT_KEY: str = str(os.getenv("WEBPEDITOR_SALT_KEY"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = bool(int(str(os.getenv("DEBUG"))))

APP_VERSION: str = str(os.getenv("APP_VERSION"))

ALLOWED_HOSTS: list[str] = ["127.0.0.1", "localhost", "webpeditor.fly.dev"]

CSRF_TRUSTED_ORIGINS: list[str] = str(os.getenv("CSRF_TRUSTED_ORIGINS")).split(",")

INSTALLED_APPS: list[str] = [
    "daphne",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_extensions",
    "silk",
    "corsheaders",
    "compressor",
    "crispy_forms",
    "crispy_tailwind",
    "cloudinary",
    "cloudinary_storage",
    "ninja_extra",
    "webpeditor_app",
]

CORS_ORIGIN_WHITELIST: list[str] = str(os.getenv("CORS_ORIGIN_WHITELIST")).split(",")

MIDDLEWARE: list[str | Any] = [
    "webpeditor_app.middlewares.error_handling_middleware.ErrorHandlingMiddleware",
    "silk.middleware.SilkyMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
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

ASGI_APPLICATION = "webpeditor.asgi.application"

FILE_UPLOAD_MAX_MEMORY_SIZE: int = 10_485_760 * 4

DATA_UPLOAD_MAX_MEMORY_SIZE: int = 52_428_800 * 4

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

# Path for future migrations
MIGRATION_MODULES: dict[str, str] = {"webpeditor_app": "webpeditor_app.infrastructure.database.migrations"}

# Password validation

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
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

LANGUAGE_CODE: str = "en-us"

TIME_ZONE: str = "UTC"

USE_I18N: bool = True

USE_TZ: bool = True

# TODO: change to real EmailBackend
EMAIL_BACKEND: str = "django.core.mail.backends.console.EmailBackend"

# Session handling
SESSION_SAVE_EVERY_REQUEST: bool = True
SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = True
SESSION_COOKIE_SAMESITE: str = "Strict"
SESSION_COOKIE_HTTPONLY: bool = True
SESSION_COOKIE_SECURE: bool = True
SESSION_COOKIE_AGE: int = int(timedelta(minutes=15).total_seconds())  # 15 minutes

# CSRF
CSRF_COOKIE_SAMESITE: str = "Strict"
CSRF_COOKIE_SECURE: bool = True
CSRF_COOKIE_AGE: int = int(timedelta(minutes=15).total_seconds())  # 15 minutes

# HSTS
SECURE_HSTS_SECONDS: int = int(timedelta(days=365 * 5).total_seconds())  # 5 year
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True
# SECURE_SSL_REDIRECT: bool = True

# Additional security settings
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
X_FRAME_OPTIONS: str = "SAMEORIGIN"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STORAGES: dict[str, dict[str, str]] = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

STATIC_URL: str = "static/"

STATIC_ROOT: Path = BASE_DIR / "static"

STATICFILES_FINDERS: list[str] = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_ENABLED: bool = True if DEBUG else False

MEDIA_URL: str = "/"

# Cloudinary storage config
CLOUDINARY_STORAGE: dict[str, Any] = {
    "CLOUD_NAME": str(os.getenv("CLOUDINARY_CLOUD_NAME")),
    "API_KEY": str(os.getenv("CLOUDINARY_API_KEY")),
    "API_SECRET": str(os.getenv("CLOUDINARY_API_SECRET")),
    "SECURE": True,
}

FILENAME_MAX_SIZE: int = 255

RESERVED_WINDOWS_FILENAMES: set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# Application definition
APP_VERBOSE_NAME: str = f"{str(WebpeditorAppConfig.verbose_name)} - V{APP_VERSION}"

CRISPY_ALLOWED_TEMPLATE_PACKS: str = "tailwind"
CRISPY_TEMPLATE_PACK: str = "tailwind"

# Jazzmin settings
JAZZMIN_SETTINGS: dict[str, Any] = {
    "site_title": f"{APP_VERBOSE_NAME} Admin",
    "site_header": APP_VERBOSE_NAME,
    "site_brand": APP_VERBOSE_NAME,
    "site_logo": "logo/pixoicon_32x32.svg",
    "login_logo": "logo/pixoicon_100x100.svg",
    "login_logo_dark": None,
    "site_logo_classes": "img-square",
    "site_icon": "logo/pixoicon_32x32.svg",
    "welcome_sign": f"Welcome to {APP_VERBOSE_NAME}",
    "copyright": "Temirkhan Amanzhanov - WebP Editor",
    "search_model": [
        "webpeditor_app.OriginalImageAsset",
        "webpeditor_app.EditedImageAsset",
        "webpeditor_app.ConvertedImageAsset",
    ],
    "user_avatar": None,
    "topmenu_links": [
        {
            "name": "Home",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        {"model": "auth.User"},
        {"model": "auth.Group"},
        {"app": "webpeditor_app"},
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "new_window": True,
        },
    ],
    "usermenu_links": [
        {"model": "auth.User"},
        {"model": "auth.Group"},
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "icon": "fa-solid fa-question",
            "new_window": True,
        },
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "webpeditor_app"],
    "custom_links": {},
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "webpeditor_app.AppUser": "fas fa-user",
        "webpeditor_app.EditorOriginalImageAsset": "fa-regular fa-images",
        "webpeditor_app.EditorOriginalImageAssetFile": "fa-regular fa-file-image",
        "webpeditor_app.EditorEditedImageAsset": "fa-regular fa-object-group",
        "webpeditor_app.EditorEditedImageAssetFile": "fa-solid fa-file-pen",
        "webpeditor_app.ConverterImageAsset": "fa-solid fa-arrow-right-arrow-left",
        "webpeditor_app.ConverterConvertedImageAssetFile": "fa-solid fa-file-code",
        "webpeditor_app.ConverterOriginalImageAssetFile": "fa-solid fa-file-code",
        "otp_totp.TOTPDevice": "fa-solid fa-shield",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS: dict[str, Any] = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": False,
}

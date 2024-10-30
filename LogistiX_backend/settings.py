# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

"""
Django settings for LogistiX_backend project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os.path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-this_is_a_dummy_key_0123'
if(os.path.isfile("LogistiX_backend/django_secret.key")):
    with open("LogistiX_backend/django_secret.key") as key_file:
        SECRET_KEY = key_file.read().strip()

if("dummy" in SECRET_KEY):
    print("LogistiX_backend/django_secret.key file not present. Still using the dummy key!")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_q',
    'colorfield',
    'rest_framework',
    'main_menu',
    'warroom',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'LogistiX_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'LogistiX_backend/templates'],
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

WSGI_APPLICATION = 'LogistiX_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    #'gameRules': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'game_rules.sqlite3',
    #}
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Login
LOGIN_REDIRECT_URL = "/menu"
LOGOUT_REDIRECT_URL = "/menu"


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Emailing settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = 'dummy@example.com'
EMAIL_HOST_USER = 'dummy@example.com'
EMAIL_HOST_PASSWORD = 'dummy_key'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
PASSWORD_RESET_TIMEOUT = 3600 # 1h

if(os.path.isfile("LogistiX_backend/email.key")):
    with open("LogistiX_backend/email.key") as key_file:
        lines = key_file.readlines()
        EMAIL_FROM = lines[0].strip()
        EMAIL_HOST_USER = lines[0].strip()
        EMAIL_HOST_PASSWORD = lines[1].strip()

if("dummy" in EMAIL_FROM or "dummy" in EMAIL_HOST_PASSWORD):
    print("Email config file not present. Still using dummy settings!")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django Q settings:
Q_CLUSTER = {
    'name': 'LogistiX',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'compress': False,
    'save_limit': 250,
    'queue_limit': 5,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'catch_up': False,
    'orm': 'default', # use Django's ORM and the underlying DB
    'poll': 0.2 # poll broker every X seconds
}


# custom settings:
N_SIDES=2



"""
Django settings for Guardian Desk project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- PRODUCTION/DEVELOPMENT SWITCH ---

# SECRET_KEY: Uses a secure environment variable on Render, falls back to default locally.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-&rckb)ef@1-24kqj6j+h__5gd6#mj$*^mk!58v$!cmj=rwj&s')

# DEBUG: True if running locally, False if running on Render.
DEBUG = 'RENDER' not in os.environ

# ALLOWED_HOSTS: Allows all hosts for deployment simplicity.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party/Local apps
    'tickets',          
    'rest_framework',   
    'corsheaders',      
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Your templates folder location
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- FINAL CUSTOM & DRF SETTINGS ---

CORS_ALLOW_ALL_ORIGINS = True
AUTH_USER_MODEL = 'tickets.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication', 
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# --- STATIC & MEDIA FILES (Local and Production) ---

# URL to serve static files
STATIC_URL = '/static/' 

# Directory where collectstatic gathers files for production (Render requires this)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Where Django looks for static files during development
STATICFILES_DIRS = [
    BASE_DIR, 
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
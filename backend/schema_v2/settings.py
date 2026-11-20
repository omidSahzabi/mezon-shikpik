"""Isolated Schema V2 database settings; deliberately no legacy API routes."""
import os

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'schema_v2']
AUTH_USER_MODEL = 'schema_v2.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'mezon_lms', 'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
    'PORT': os.environ.get('POSTGRES_PORT', '55432'),
    'USER': os.environ.get('POSTGRES_USER', 'mezon_app'),
    'PASSWORD': os.environ['POSTGRES_PASSWORD'],
}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher']
USE_TZ = True
TIME_ZONE = 'Asia/Tehran'
LANGUAGE_CODE = 'fa-ir'

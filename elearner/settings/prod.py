import os
from dotenv import load_dotenv
from pathlib import Path

# load .env file
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('APP_SECRET_KEY')
EMAIL_HOST_PASSWORD = os.getenv('APP_EMAIL_PASSWORD')  # Gmail account App Password

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['elearner.moamin.dev']

ADMINS = [
    ("Mostafa Amin", "mamostafamin@gmail.com")
]

MANAGERS = ADMINS

# add security settings

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# if you're using reverse proxy such as nginx and this is set to True, django would not redirect http requests from nginx. 
# so we let nginx handles the redirection to https
# SECURE_SSL_REDIRECT = True # redirect to https if attempted to access via http

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://elearner.moamin.dev']
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'uploads'

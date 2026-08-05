import os
from pathlib import Path
import dj_database_url

# প্রজেক্টের রুট ডিরেক্টরি
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ সতর্কবার্তা: প্রোডাকশনে নিরাপদ SECRET_KEY ব্যবহার করুন।
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')

DEBUG = True

ALLOWED_HOSTS = ['*']


# অ্যাপলিকেশন ডেফিনিশন
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # আপনার কাস্টম অ্যাপ
    'bills',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jute_ledger.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'jute_ledger.wsgi.application'


# ডাটাবেজ কনফিগারেশন (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jute_db',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Render Cloud PostgreSQL setup
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )


# পাসওয়ার্ড ভ্যালিডেশন
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


# আন্তর্জাতিকীকরণ (Internationalization)
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# স্ট্যাটিক ও মিডিয়া ফাইল কনফিগারেশন
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise দিয়ে কম্প্রেসড ও ক্যাশড স্ট্যাটিক ফাইল হ্যান্ডলিং
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ইউজার আপলোড করা ফাইলের জন্য
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ডিফল্ট প্রাইমারি কি ফিল্ড টাইপ
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🎯 Redirect Settings
LOGIN_REDIRECT_URL = 'grade_entry'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
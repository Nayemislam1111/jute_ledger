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
    # 👑 Jazzmin (Admin Panel Design - admin-এর ওপরে রাখতে হবে)
    'jazzmin',
    
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

# WhiteNoise দিয়ে স্ট্যাটিক ফাইল হ্যান্ডলিং (Staticfiles storage clean implementation)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ইউজার আপলোড করা ফাইলের জন্য
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ডিফল্ট প্রাইমারি কি ফিল্ড টাইপ
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🎯 Redirect Settings
LOGIN_REDIRECT_URL = 'grade_entry'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'


# ==========================================
# 🏢 AKIJ GROUP ADMIN PANEL CUSTOMIZATION (JAZZMIN)
# ==========================================

JAZZMIN_SETTINGS = {
    # Title & Branding
    "site_title": "Akij Group Admin",
    "site_header": "Akij Group Administration",
    "site_brand": "Akij Group Administration",
    "welcome_sign": "Welcome to Akij Group Administration",
    "copyright": "Akij Group Ltd",
    
    # 🎯🎯 কাস্টম CSS ও JS ফাইল লিংক (এটি যুক্ত করা হলো) 🎯🎯
    "custom_css": "admin_custom/motion.css",
    "custom_js": "admin_custom/motion.js",
    
    # Top Menu Links
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Main Site", "url": "/grade-entry/"},
    ],

    # Navigation & Sidebar
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Model Icons
    "icons": {
        "auth": "fas fa-user-shield",
        "auth.user": "fas fa-user-cog",
        "auth.Group": "fas fa-users-cog",
        "bills.BillEntry": "fas fa-file-invoice-dollar",
        "bills.GradeEntry": "fas fa-layer-group",
        "bills.JuteRate": "fas fa-chart-line",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-angle-right",
    
    # Modal Popups
    "related_modal_active": True,
    "use_google_fonts_booster": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-info",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "theme": "pulse",
    "dark_mode_theme": None,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_flat_style": False,
}
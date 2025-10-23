# arttoy_project/settings.py

from pathlib import Path
import os
from django.utils import timezone 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9dnt%9o1=u)i5!(qfwoj+r&cb5==cxr=m56d5yi(qkx(fq1at('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin', # ทำความสะอาดบรรทัดนี้แล้ว (Jazzmin ต้องอยู่บนสุด)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'shop',
    'widget_tweaks',
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

ROOT_URLCONF = 'arttoy_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'arttoy_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bangkok' 

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files (User uploaded images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication settings
LOGIN_URL = '/login/' 
LOGIN_REDIRECT_URL = '/login/redirect/' 


# ----------------------------------------------------------------------
# 🎨 JAZZMIN CONFIGURATION (สำหรับตกแต่งหน้า Admin)
# ----------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    # TITLE & LOGO
    "site_title": "Art Toy Shop Admin", 
    "site_header": "Art Toy Shop",
    "site_brand": "Admin Console",
    "welcome_sign": "ยินดีต้อนรับสู่ Art Toy Shop Admin",

    # UI/UX OPTIONS
    "topbar_fixed": False,
    "sidebar_fixed": True,
    "theme": "united",

    # CUSTOM LINKS & MENU
    "usermenu_links": [
        {"name": "ดูหน้าหลัก", "url": "shop:index", "new_window": True},
        {"model": "auth.user"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # เมนูหลักใน Sidebar
    "order_with_respect_to": ["auth", "shop.product", "shop.order", "shop.payment"],
    "custom_links": {
        # 💡 ใช้ URL Name ที่ถูกต้อง (shop:...)
        "shop": [ 
            {
                "name": "ดู Admin Dashboard",
                "url": "shop:admin_dashboard", 
                "icon": "fas fa-chart-line",
            },
            {
                "name": "จัดการสินค้า (Custom)",
                "url": "shop:manage_products", 
                "icon": "fas fa-boxes",
            },
            {
                "name": "จัดการคำสั่งซื้อ (Custom)",
                "url": "shop:manage_orders", 
                "icon": "fas fa-receipt",
            },
        ]
    }
}
# ----------------------------------------------------------------------
# END JAZZMIN CONFIGURATION
# ----------------------------------------------------------------------
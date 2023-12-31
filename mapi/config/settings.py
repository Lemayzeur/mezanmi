from corsheaders.defaults import default_headers
from pathlib import Path
from decouple import config, Csv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG") == 'True'

ALLOWED_HOSTS = [] if DEBUG else [config('MAIN_HOST')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'drf_yasg',
    
    'apps.core.config.CoreConfig',
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

ROOT_URLCONF = 'config.endpoints'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'  # Change this to America/Port-au-Prince for example

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MONCASH_CLIENT_ID = config('MONCASH_CLIENT_ID')
MONCASH_SECRET_KEY = config('MONCASH_SECRET_KEY') 
MONCASH_QUERY_KEY = 'transactionId'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.authentication.SafeJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'config.permissions.IsAuthenticated',
    ],
    # 'DATETIME_FORMAT':'%s',
    'DEFAULT_THROTTLE_CLASSES': [
        'config.throttling.SafeAnonRateThrottle',
        'config.throttling.SafeUserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '40/minute'
    },
    # 'EXCEPTION_HANDLER': 'api.exception_handler.custom_exception_handler'
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:41739",
    "http://127.0.0.1",
    'http://192.168.1.144:8080',
    'http://mezanmi.pythonanywhere.com'
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-Client-ID',
]

EXCHANGE_RATE = {
    'ALLOWED_BACKENDS': [
        'config.exchange_rate.ExchangeRateBackend',
    ],
    'PATH': BASE_DIR / '.rate',
    'API_KEY': config("EXCHANGE_RATE_API_KEY"),
    'SYSTEM': 'CUSTOM', # it can be 'CUSTOM', 'BRH', or 'API'
    # Get an API KEY here: https://app.exchangerate-api.com/
    'CUSTOM': {
        'HTG': 1,
        'USD': 134.4502,
        'EUR': 135.3400,
    }
    
}
from pathlib import Path
from decouple import config as env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # local apps
    'apps.accounts.apps.UsersConfig',
    'apps.shared.apps.SharedConfig',
    'apps.member.apps.MemberConfig',
    'apps.jurisdiction.apps.JurisdictionConfig',
    'apps.events.apps.EventsConfig',
    'apps.transaction.apps.TransactionConfig',
    'apps.donation.apps.DonationConfig',
    'apps.content.apps.ContentConfig',

    # third party apps
    'rest_framework',
    'django_extensions',
    'rest_framework_simplejwt.token_blacklist',
    'storages',
    'corsheaders',
    'django_filters',
    'simple_history',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'acci.urls'

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

WSGI_APPLICATION = 'acci.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'ATOMIC_REQUESTS': True,

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

APPEND_SLASH = False

ENVIRONMENT = env('ENVIRONMENT')
# REST configuration
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [

        'rest_framework.throttling.AnonRateThrottle',

        'rest_framework.throttling.UserRateThrottle'

    ],
    'DEFAULT_THROTTLE_RATES': {

        'anon': '60/min',

        'user': '120/min'

    },
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'apps.shared.utils.renderer.CustomJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

INTERNAL_HOST = env('INTERNAL_HOST')

ASGI_APPLICATION = 'acci.asgi.application'

PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY')
PAYSTACK_URL = "https://api.paystack.co/"

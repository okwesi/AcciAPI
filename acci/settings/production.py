from datetime import timedelta

from acci.settings.base import *

ALLOWED_HOSTS = []
DEBUG = True
ENVIRONMENT = env('ENVIRONMENT')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=120),
}
CSRF_TRUSTED_ORIGINS = []
STATIC_URL = f''
# Media files
MEDIA_URL = f''
CORS_ALLOW_ALL_ORIGINS = True
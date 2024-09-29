from datetime import timedelta

from acci.settings.base import *

DEBUG = env('DEBUG', cast=bool)
# ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='*', cast=Csv())
ALLOWED_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0', "158.178.200.22:8000")
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://0.0.0.0:8000',
    'http://127.0.0.1:0000',
    'http://127.0.0.1:3000',
    'http://0.0.0.0:3000',
    'http://localhost:3000',
]
DEBUG = True
ENVIRONMENT = env('ENVIRONMENT')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=120),
}
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
STATIC_URL = f'/static/'
# Media files
MEDIA_URL = f'/media/'

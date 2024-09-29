from datetime import timedelta

from acci.settings.base import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', "158.178.200.22"]
CORS_ALLOWED_ORIGINS = [
    'https://local.scanport.com',
    'http://stage.accihq.org',
    'http://158.178.200.22:8000',
    'http://localhost:3000',
]
DEBUG = True
ENVIRONMENT = env('ENVIRONMENT')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=120),
}
CSRF_TRUSTED_ORIGINS = ['https://stage.accihq.org', 'http://158.178.200.22:3000',]
STATIC_URL = f'/static/'
# Media files
MEDIA_URL = f'/media/'

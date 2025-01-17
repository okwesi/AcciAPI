from datetime import timedelta

from acci.settings.base import *

DEBUG = env('DEBUG', cast=bool)
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = [
    'https://local.scanport.com',
    'https://stage.accihq.org',
    'http://158.178.200.22:8000',
    'http://localhost:3000',
    "https://backend.accihq.org",
]
DEBUG = True
ENVIRONMENT = env('ENVIRONMENT')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=120),
}
CSRF_TRUSTED_ORIGINS = ['https://stage.accihq.org', 'http://158.178.200.22:3000', "https://backend.accihq.org", ]
# STATIC_URL = f'/static/'
# # Media files
# MEDIA_URL = f'/media/'

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', None)
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', None)

# extra static and media file settings.
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'


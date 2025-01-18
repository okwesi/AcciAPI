from acci.settings.base import *

from datetime import timedelta
from datetime import timedelta

from acci.settings.base import *

DEBUG = env('DEBUG', cast=bool)
# ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='*', cast=Csv())
ALLOWED_HOSTS = ["*"]
ENVIRONMENT = env('ENVIRONMENT')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=120),
}
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"
]
# AWS S3 configuration
CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://*"
]
# extra static and media file settings.
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', None)
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_CUSTOM_DOMAIN = "iyfconnect-backend-local.s3.us-east-1.amazonaws.com"
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'




# STATIC_URL = f'/static/'
# # Media files
# MEDIA_URL = f'/media/'



from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens(user):
    """
    Generate access and refresh tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }

def get_api_base_url():
    """
    Get the base URL for the API.
    """
    environment = settings.ENVIRONMENT
    url_mapping = {
        'local':'local.scanport.app',
        'staging':'backend-dev.scanport.app',
        'production':'backend.scanport.app'
    }

    return f'https://{url_mapping[environment]}'




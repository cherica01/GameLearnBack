# api/authentication.py
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that adds additional validation.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed as e:
            raise AuthenticationFailed(_('Invalid token or expired token.'))


class ApiKeyAuthentication(BasicAuthentication):
    """
    Custom authentication for API keys.
    """
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        # Validate API key against database
        try:
            from accounts.models import ApiKey
            api_key_obj = ApiKey.objects.get(key=api_key, is_active=True)
            return (api_key_obj.user, None)
        except:
            return None
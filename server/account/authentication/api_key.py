from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()


class ApiKeyAuthentication(BaseAuthentication):
    """API Key Authentication"""

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        try:
            user = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

        if not user.is_active:
            raise AuthenticationFailed('User account is inactive')

        return user, None

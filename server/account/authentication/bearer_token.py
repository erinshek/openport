from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class BearerTokenAuthentication(BaseAuthentication):
    """Bearer Token Authentication"""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

        if not token_obj.user.is_active:
            raise AuthenticationFailed('User account is inactive')

        return token_obj.user, token_obj

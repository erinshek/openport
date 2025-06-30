import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class ApiKeyMiddleware(MiddlewareMixin):
    """API Key authentication middleware"""

    def process_request(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            try:
                user = User.objects.get(api_key=api_key)
                request.user = user
                logger.info(f"Authentication with API key: {user.username}")
            except User.DoesNotExist:
                logger.warning(f"Invalid API key: {api_key[:10]}...")

        return None

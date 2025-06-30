import logging

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from account.serializers.user import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': True,
            'message': 'User registered successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data.get('user')

        user_ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                   request.META.get('REMOTE_ADDR'))
        user.last_login_ip = user_ip
        user.save()

        token, created = Token.objects.get_or_create(user=user)

        logger.info(f"User logged in: {user.username} {user_ip}")

        return Response({
            'success': True,
            'message': 'User logged in',
            'data': {
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'api_key': user.api_key,
            }
        })

    return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        logger.info(f"User logged out: {request.user.username}")
        return Response({
            'success': True,
            'message': 'User logged out',
            'data': None
        })
    except:
        return Response({
            'success': False,
            'message': 'User logged out',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_me(request):
    return Response({
        'success': True,
        'message': 'User profile data',
        'data': UserProfileSerializer(request.user).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_api_key(request):
    user = request.user
    new_api_key = user.regenerate_api_key()
    user.save()

    logger.info(f"API key regenerated for user: {user.username}")

    return Response({
        'success': True,
        'message': 'API key regenerated',
        'data': {
            'api_key': new_api_key
        }
    })

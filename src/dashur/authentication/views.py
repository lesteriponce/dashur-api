"""
API views for authentication app.
"""
import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils import api_response
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer, PasswordChangeSerializer, UserSerializer
)

User = get_user_model()
logger = logging.getLogger('dashur')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Register a new user.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        logger.info(f"User registered: {user.email} from IP: {get_client_ip(request)}")
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return api_response(
            success=True,
            data={
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            message="Registration successful",
            status_code=status.HTTP_201_CREATED
        )
    
    return api_response(
        success=False,
        message="Registration failed",
        errors=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Login user and return JWT tokens.
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        logger.info(f"User login: {user.email} from IP: {get_client_ip(request)}")
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return api_response(
            success=True,
            data={
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            message="Login successful"
        )
    
    return api_response(
        success=False,
        message="Login failed",
        errors=serializer.errors,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """
    Logout user by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out: {request.user.email}")
            
            return api_response(
                success=True,
                message="Logout successful"
            )
        else:
            return api_response(
                success=False,
                message="Refresh token required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return api_response(
            success=False,
            message="Logout failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """
    Get user profile information.
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return api_response(
            success=True,
            data=serializer.data,
            message="Profile retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to retrieve profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """
    Update user profile information.
    """
    try:
        profile = request.user.profile
        serializer = UserProfileUpdateSerializer(
            profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated: {request.user.email}")
            
            # Return updated profile data
            updated_profile = UserProfileSerializer(profile)
            return api_response(
                success=True,
                data=updated_profile.data,
                message="Profile updated successfully"
            )
        
        return api_response(
            success=False,
            message="Profile update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to update profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password.
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Password changed: {request.user.email}")
        
        return api_response(
            success=True,
            message="Password changed successfully"
        )
    
    return api_response(
        success=False,
        message="Password change failed",
        errors=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """
    Get basic user information.
    """
    serializer = UserSerializer(request.user)
    return api_response(
        success=True,
        data=serializer.data,
        message="User information retrieved successfully"
    )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view with consistent response format.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return api_response(
                success=True,
                data=response.data,
                message="Token refreshed successfully"
            )
        except Exception as e:
            return api_response(
                success=False,
                message="Token refresh failed",
                errors={'detail': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )

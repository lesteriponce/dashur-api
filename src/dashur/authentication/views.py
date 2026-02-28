"""
API views for authentication app.
"""
import logging
import secrets
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.sessions.models import Session
from dashur.utils import api_response, get_client_ip
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer, PasswordChangeSerializer, UserSerializer,
    CMSLoginSerializer, CMSUserSerializer, CMSSessionSerializer
)
from .models import CMSUser, CMSSession

User = get_user_model()
logger = logging.getLogger('dashur')


@extend_schema(
    request=UserRegistrationSerializer,
    responses={201: UserSerializer},
    description="Register a new user"
)
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


@extend_schema(
    request=UserLoginSerializer,
    responses={200: UserSerializer},
    description="Login user and return JWT tokens"
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


# CMS Authentication Views

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def cms_login(request):
    """
    CMS login using session authentication for API documentation access.
    """
    serializer = CMSLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        cms_user = serializer.validated_data['cms_user']
        
        # Create Django session
        from django.contrib.auth import login
        login(request, user)
        
        # Create CMS session record
        session_key = request.session.session_key or secrets.token_hex(20)
        cms_session, created = CMSSession.objects.get_or_create(
            cms_user=cms_user,
            session_key=session_key,
            defaults={
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        if not created:
            # Update existing session
            cms_session.ip_address = get_client_ip(request)
            cms_session.user_agent = request.META.get('HTTP_USER_AGENT', '')
            cms_session.is_active = True
            cms_session.last_activity = timezone.now()
            cms_session.save()
        
        logger.info(f"CMS login: {user.email} from IP: {get_client_ip(request)}")
        
        return api_response(
            success=True,
            data={
                'cms_user': CMSUserSerializer(cms_user).data,
                'session_key': session_key,
            },
            message="CMS login successful"
        )
    
    return api_response(
        success=False,
        message="CMS login failed",
        errors=serializer.errors,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cms_logout(request):
    """
    CMS logout by deactivating the session.
    """
    try:
        # Deactivate CMS session
        session_key = request.session.session_key
        if session_key:
            CMSSession.objects.filter(
                cms_user__user=request.user,
                session_key=session_key,
                is_active=True
            ).update(is_active=False)
        
        # Logout Django session
        from django.contrib.auth import logout
        logout(request)
        
        logger.info(f"CMS logout: {request.user.email}")
        
        return api_response(
            success=True,
            message="CMS logout successful"
        )
    except Exception as e:
        logger.error(f"CMS logout error: {str(e)}")
        return api_response(
            success=False,
            message="CMS logout failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cms_profile(request):
    """
    Get CMS user profile information.
    """
    try:
        cms_user = request.user.cms_user
        serializer = CMSUserSerializer(cms_user)
        return api_response(
            success=True,
            data=serializer.data,
            message="CMS profile retrieved successfully"
        )
    except CMSUser.DoesNotExist:
        return api_response(
            success=False,
            message="CMS user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"CMS profile retrieval error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to retrieve CMS profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cms_sessions(request):
    """
    Get active CMS sessions for the current user.
    """
    try:
        cms_user = request.user.cms_user
        sessions = CMSSession.objects.filter(
            cms_user=cms_user,
            is_active=True
        ).order_by('-last_activity')
        
        serializer = CMSSessionSerializer(sessions, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="CMS sessions retrieved successfully"
        )
    except CMSUser.DoesNotExist:
        return api_response(
            success=False,
            message="CMS user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"CMS sessions retrieval error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to retrieve CMS sessions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cms_revoke_session(request, session_key):
    """
    Revoke a specific CMS session.
    """
    try:
        cms_user = request.user.cms_user
        
        # Don't allow revoking current session
        current_session_key = request.session.session_key
        if session_key == current_session_key:
            return api_response(
                success=False,
                message="Cannot revoke current session",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Revoke the session
        revoked_count = CMSSession.objects.filter(
            cms_user=cms_user,
            session_key=session_key,
            is_active=True
        ).update(is_active=False)
        
        if revoked_count == 0:
            return api_response(
                success=False,
                message="Session not found or already revoked",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"CMS session revoked: {session_key} by {request.user.email}")
        
        return api_response(
            success=True,
            message="CMS session revoked successfully"
        )
    except CMSUser.DoesNotExist:
        return api_response(
            success=False,
            message="CMS user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"CMS session revocation error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to revoke CMS session",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

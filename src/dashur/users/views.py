"""
Views for the users app.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from dashur.utils import api_response, get_client_ip
from .models import UserActivity, UserSession, UserPreference
from .serializers import UserActivitySerializer, UserSessionSerializer, UserPreferenceSerializer

User = get_user_model()


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user activities.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-timestamp')


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user sessions.
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user).order_by('-last_activity')


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user preferences.
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj


class UserActivityListView(APIView):
    """
    API view to get user activity log.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's recent activities."""
        activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:50]
        serializer = UserActivitySerializer(activities, many=True)
        
        return api_response(
            success=True,
            data=serializer.data,
            message="Activity log retrieved successfully"
        )


class UserPreferenceView(APIView):
    """
    API view to manage user preferences.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user preferences."""
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        serializer = UserPreferenceSerializer(preferences)
        
        return api_response(
            success=True,
            data=serializer.data,
            message="Preferences retrieved successfully"
        )
    
    def patch(self, request):
        """Update user preferences."""
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        serializer = UserPreferenceSerializer(preferences, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Log the preference update
            UserActivity.objects.create(
                user=request.user,
                action='preferences_updated',
                description='User updated their preferences',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return api_response(
                success=True,
                data=serializer.data,
                message="Preferences updated successfully"
            )
        
        return api_response(
            success=False,
            message="Failed to update preferences",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_activity(request):
    """
    Log user activity programmatically.
    """
    action = request.data.get('action')
    description = request.data.get('description', '')
    
    if not action:
        return api_response(
            success=False,
            message="Action is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    activity = UserActivity.objects.create(
        user=request.user,
        action=action,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    serializer = UserActivitySerializer(activity)
    
    return api_response(
        success=True,
        data=serializer.data,
        message="Activity logged successfully",
        status_code=status.HTTP_201_CREATED
    )

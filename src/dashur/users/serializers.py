"""
Serializers for the users app.
"""
from rest_framework import serializers
from .models import UserActivity, UserSession, UserPreference


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity logs.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ('id', 'user', 'user_email', 'action', 'description', 'ip_address', 
                 'user_agent', 'timestamp')
        read_only_fields = ('id', 'user', 'timestamp')


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user sessions.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    session_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = ('id', 'user', 'user_email', 'session_key', 'ip_address', 'user_agent',
                 'is_active', 'created_at', 'last_activity', 'session_duration')
        read_only_fields = ('id', 'user', 'session_key', 'created_at', 'last_activity')
    
    def get_session_duration(self, obj):
        """Calculate session duration."""
        if obj.created_at and obj.last_activity:
            duration = obj.last_activity - obj.created_at
            return str(duration).split('.')[0]  # Remove microseconds
        return None


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserPreference
        fields = ('id', 'user', 'user_email', 'language', 'timezone', 'email_notifications',
                 'push_notifications', 'marketing_emails', 'theme', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

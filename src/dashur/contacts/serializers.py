"""
Serializers for the contacts app.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import ContactSubmission, ContactResponse
from dashur.utils import get_client_ip
from typing import Dict, Any


class ContactSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for contact submissions.
    """
    full_name = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    
    @extend_schema_field(str)
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @extend_schema_field(bool)
    def is_new(self) -> bool:
        return self.status == 'new'
    
    @extend_schema_field(bool)
    def is_urgent(self) -> bool:
        return self.priority == 'urgent'
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'company',
            'subject', 'message', 'priority', 'status', 'referral_source',
            'newsletter_subscription', 'created_at', 'updated_at', 'is_new', 'is_urgent'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'is_new', 'is_urgent']


class ContactSubmissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact submissions.
    """
    class Meta:
        model = ContactSubmission
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company', 'subject',
            'message', 'priority', 'referral_source', 'newsletter_subscription'
        ]
    
    def validate_email(self, value):
        """Validate email format and check for spam."""
        # Basic email validation is handled by EmailField
        # Add additional spam checks if needed
        return value
    
    def validate_message(self, value):
        """Validate message content."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value
    
    def create(self, validated_data):
        """Create contact submission with additional metadata."""
        request = self.context.get('request')
        
        # Add IP address and user agent
        if request:
            validated_data['ip_address'] = get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)


class ContactSubmissionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating contact submissions (admin use).
    """
    class Meta:
        model = ContactSubmission
        fields = ['status', 'priority', 'notes']
    
    def validate_status(self, value):
        """Validate status change."""
        if self.instance and self.instance.status == value:
            raise serializers.ValidationError("Status is already set to this value")
        return value


class ContactResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for contact responses.
    """
    responded_by_name = serializers.CharField(source='responded_by.get_full_name', read_only=True)
    submission_info = serializers.SerializerMethodField()
    
    @extend_schema_field(Dict[str, Any])
    def get_submission_info(self, obj) -> Dict[str, Any]:
        """Get basic submission information."""
        return {
            'id': obj.submission.id,
            'name': obj.submission.full_name,
            'email': obj.submission.email,
            'subject': obj.submission.subject,
            'created_at': obj.submission.created_at
        }
    
    class Meta:
        model = ContactResponse
        fields = [
            'id', 'submission', 'submission_info', 'responded_by', 'responded_by_name',
            'response_message', 'response_email_sent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'responded_by', 'created_at', 'updated_at']


class ContactResponseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact responses.
    """
    class Meta:
        model = ContactResponse
        fields = ['submission', 'response_message']
    
    def validate_submission(self, value):
        """Validate that submission exists and is not already responded."""
        if hasattr(value, 'response'):
            raise serializers.ValidationError("This submission has already been responded to")
        return value
    
    def create(self, validated_data):
        """Create response with authenticated user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['responded_by'] = request.user
        
        return super().create(validated_data)


class ContactSubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for contact submissions including response.
    """
    response = ContactResponseSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'company',
            'subject', 'message', 'priority', 'status', 'ip_address', 'user_agent',
            'referral_source', 'newsletter_subscription', 'notes', 'created_at',
            'updated_at', 'response', 'is_new', 'is_urgent'
        ]
        read_only_fields = [
            'id', 'ip_address', 'user_agent', 'created_at', 'updated_at',
            'response', 'is_new', 'is_urgent'
        ]


class ContactSubmissionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for contact submission lists.
    """
    full_name = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'full_name', 'email', 'subject', 'priority', 'status',
            'created_at', 'is_new', 'is_urgent'
        ]

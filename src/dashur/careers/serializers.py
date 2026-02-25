"""
Serializers for the careers app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobPosition, JobApplication, ApplicationStatusHistory
from dashur.utils import validate_file_upload

User = get_user_model()


class JobPositionSerializer(serializers.ModelSerializer):
    """
    Serializer for job positions.
    """
    salary_range = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    application_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'department', 'employment_type', 'status', 'description',
            'requirements', 'responsibilities', 'benefits', 'salary_min', 'salary_max',
            'salary_range', 'location', 'remote_work', 'experience_years', 
            'education_level', 'application_deadline', 'is_featured', 'created_at', 
            'updated_at', 'is_active', 'application_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'application_count']


class JobPositionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating job positions (admin use).
    """
    class Meta:
        model = JobPosition
        fields = [
            'title', 'department', 'employment_type', 'status', 'description',
            'requirements', 'responsibilities', 'benefits', 'salary_min', 'salary_max',
            'location', 'remote_work', 'experience_years', 'education_level',
            'application_deadline', 'is_featured'
        ]
    
    def validate(self, data):
        """Validate salary range."""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Minimum salary cannot be greater than maximum salary"
            )
        
        return data


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for job applications.
    """
    position_title = serializers.CharField(source='position.title', read_only=True)
    department = serializers.CharField(source='position.department', read_only=True)
    full_name = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'user', 'position', 'position_title', 'department', 'first_name',
            'last_name', 'full_name', 'email', 'phone', 'resume', 'cover_letter',
            'linkedin_profile', 'portfolio', 'expected_salary', 'available_start_date',
            'status', 'applied_at', 'updated_at', 'is_pending'
        ]
        read_only_fields = ['id', 'user', 'applied_at', 'updated_at', 'is_pending']


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating job applications.
    """
    class Meta:
        model = JobApplication
        fields = [
            'position', 'first_name', 'last_name', 'email', 'phone', 'resume',
            'cover_letter', 'linkedin_profile', 'portfolio', 'expected_salary',
            'available_start_date'
        ]
    
    def validate_resume(self, value):
        """Validate resume file upload."""
        allowed_types = [
            'application/pdf', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        is_valid, error_message = validate_file_upload(
            value, 
            allowed_types=allowed_types, 
            max_size_mb=5
        )
        
        if not is_valid:
            raise serializers.ValidationError(error_message)
        
        return value
    
    def validate_position(self, value):
        """Validate that the position is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "This position is no longer accepting applications"
            )
        return value
    
    def create(self, validated_data):
        """Create application with authenticated user."""
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Check if user has already applied
        if JobApplication.objects.filter(
            user=user, 
            position=validated_data['position']
        ).exists():
            raise serializers.ValidationError(
                "You have already applied for this position"
            )
        
        return super().create(validated_data)


class JobApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating job applications (admin use).
    """
    class Meta:
        model = JobApplication
        fields = [
            'status', 'notes', 'expected_salary', 'available_start_date'
        ]
    
    def validate_status(self, value):
        """Validate status change."""
        if self.instance and self.instance.status == value:
            raise serializers.ValidationError("Status is already set to this value")
        return value


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for application status history.
    """
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id', 'old_status', 'new_status', 'changed_by', 'changed_by_name',
            'notes', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_by', 'changed_at']


class JobApplicationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for job applications including history.
    """
    position = JobPositionSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    full_name = serializers.ReadOnlyField()
    status_history = ApplicationStatusHistorySerializer(
        many=True, 
        read_only=True, 
        source='status_history.all'
    )
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'user', 'position', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'resume', 'cover_letter', 'linkedin_profile',
            'portfolio', 'expected_salary', 'available_start_date', 'status',
            'notes', 'applied_at', 'updated_at', 'status_history'
        ]
        read_only_fields = ['id', 'user', 'applied_at', 'updated_at', 'status_history']


class JobPositionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for job position lists.
    """
    salary_range = serializers.ReadOnlyField()
    application_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'department', 'employment_type', 'location',
            'remote_work', 'salary_range', 'is_featured', 'created_at',
            'application_count'
        ]

"""
Serializers for authentication app.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, CMSUser, CMSSession


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    user = serializers.StringRelatedField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('user', 'email', 'first_name', 'last_name', 'phone', 'is_verified', 
                 'date_joined', 'bio', 'avatar', 'website', 'linkedin', 'github', 
                 'location', 'resume', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    phone = serializers.CharField(source='user.phone', required=False)
    
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone', 'bio', 'avatar', 'website', 
                 'linkedin', 'github', 'location', 'resume')
    
    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for API responses.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 
                 'phone', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'email', 'is_verified', 'date_joined')


class CMSLoginSerializer(serializers.Serializer):
    """
    Serializer for CMS login.
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            # Check if user has CMS access
            try:
                cms_user = user.cms_user
                if not cms_user.has_api_access():
                    raise serializers.ValidationError('CMS access denied')
            except CMSUser.DoesNotExist:
                raise serializers.ValidationError('CMS user not found')
            
            attrs['user'] = user
            attrs['cms_user'] = cms_user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class CMSUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CMS user information.
    """
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    
    class Meta:
        model = CMSUser
        fields = ('id', 'user', 'email', 'first_name', 'last_name', 'full_name',
                 'is_active', 'is_content_manager', 'is_api_viewer', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class CMSSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for CMS session information.
    """
    cms_user = CMSUserSerializer(read_only=True)
    user_email = serializers.EmailField(source='cms_user.user.email', read_only=True)
    
    class Meta:
        model = CMSSession
        fields = ('id', 'cms_user', 'user_email', 'session_key', 'ip_address',
                 'user_agent', 'is_active', 'created_at', 'last_activity')
        read_only_fields = ('id', 'session_key', 'created_at', 'last_activity')

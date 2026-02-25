"""
Custom permissions for the Dashur API.
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or staff
        return obj.user == request.user or request.user.is_staff


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to staff
        return request.user and request.user.is_staff


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner
        return obj.user == request.user


class CanApplyToPosition(permissions.BasePermission):
    """
    Custom permission to check if user can apply to a position.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if position is active
        if hasattr(obj, 'status'):
            return obj.status == 'active'
        return True


class IsApplicationOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission for job applications.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access all applications
        if request.user.is_staff:
            return True
        
        # Users can only access their own applications
        return obj.user == request.user


class IsContactOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission for contact submissions.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access all submissions
        if request.user.is_staff:
            return True
        
        # Users can only access their own submissions (by email)
        return obj.email == request.user.email


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_verified', False)
        )

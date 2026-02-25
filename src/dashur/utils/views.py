"""
Custom view classes for different authentication requirements.
"""
from rest_framework import generics
from django.conf import settings


class AdminAPIView(generics.GenericAPIView):
    """
    Base API view that uses SessionAuthentication for admin/file upload endpoints.
    """
    def get_authenticators(self):
        """
        Use SessionAuthentication for admin endpoints.
        """
        from rest_framework.authentication import SessionAuthentication
        return [SessionAuthentication()]
    
    def get_permissions(self):
        """
        Ensure proper permissions for admin endpoints.
        """
        from rest_framework.permissions import IsAuthenticated
        return [permission() for permission in [IsAuthenticated]]
    
    def get_renderer_classes(self):
        """
        Use admin configuration for renderers.
        """
        admin_config = getattr(settings, 'REST_FRAMEWORK_ADMIN', {})
        return admin_config.get('DEFAULT_RENDERER_CLASSES', 
                              [self.renderer_classes])
    
    def get_parser_classes(self):
        """
        Use admin configuration for parsers.
        """
        admin_config = getattr(settings, 'REST_FRAMEWORK_ADMIN', {})
        return admin_config.get('DEFAULT_PARSER_CLASSES', 
                              [self.parser_classes])


class FileUploadAPIView(AdminAPIView):
    """
    Base view for file upload endpoints using SessionAuthentication.
    """
    pass  # Inherits all admin functionality

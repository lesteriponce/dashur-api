"""
Custom views for Dashur API.
"""
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication


class FileUploadAPIView(APIView):
    """
    Base API view for handling file uploads.
    Uses SessionAuthentication for file uploads.
    """
    authentication_classes = [SessionAuthentication]
    parser_classes = [MultiPartParser, FormParser]

"""
Custom middleware for the Dashur API.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from dashur.utils import get_client_ip

logger = logging.getLogger('dashur')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if settings.DEBUG:
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware.
    """
    
    def process_request(self, request):
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        # Simple rate limiting based on IP
        ip = get_client_ip(request)
        
        # This is a basic implementation - in production, use Redis or similar
        from django.core.cache import cache
        
        cache_key = f"rate_limit:{ip}"
        requests = cache.get(cache_key, 0)
        
        if requests > 100:  # 100 requests per minute
            logger.warning(f"Rate limit exceeded for IP: {ip} - Requests: {requests}/minute")
            return JsonResponse({
                'success': False,
                'message': 'Rate limit exceeded. Please try again later.',
                'errors': {'rate_limit': 'Too many requests'}
            }, status=429)
        
        # Increment counter with 1-minute expiry
        cache.set(cache_key, requests + 1, 60)
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log API requests for monitoring and debugging.
    """
    
    def process_request(self, request):
        # Log API requests
        if settings.DEBUG:
            ip = get_client_ip(request)
            method = request.method
            path = request.path
            user = getattr(request.user, 'email', 'anonymous')
            
            logger.debug(f"API Request: {method} {path} - IP: {ip} - User: {user}")
        
        return None


class APIMiddleware(MiddlewareMixin):
    """
    General API middleware for common functionality.
    """
    
    def process_request(self, request):
        # Set request attributes
        request.is_api = request.path.startswith('/api/')
        
        # Add request ID for tracking
        import uuid
        request.request_id = str(uuid.uuid4())
        
        return None
    
    def process_response(self, request, response):
        # Add request ID to response headers for debugging
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        
        return response

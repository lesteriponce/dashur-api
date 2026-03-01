"""
Custom middleware for the Dashur API.
"""
import logging
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import reverse
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


class CMSAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to protect API documentation and CMS endpoints.
    Requires CMS login for access to /api/docs and other protected endpoints.
    """
    
    # Paths that require CMS authentication
    PROTECTED_PATHS = [
        '/api/docs/',
        '/api/redoc/',
        '/api/schema/',
    ]
    
    # Paths that should never be redirected (API endpoints)
    API_PATHS = [
        '/api/auth/cms/',
        '/api/auth/',
        '/api/careers/',
        '/api/contacts/',
        '/api/admin/',
    ]
    
    def process_request(self, request):
        path = request.path
        
        # Skip CMS authentication for CMS login/logout paths
        if path.startswith('/cms/'):
            return None
        
        # Skip CMS authentication for admin paths
        if path.startswith('/admin/'):
            return None
        
        # Skip for static files and media
        if path.startswith('/static/') or path.startswith('/media/'):
            return None
        
        # Skip for API endpoints that don't need CMS protection
        for api_path in self.API_PATHS:
            if path.startswith(api_path):
                return None
        
        # Check if this is a protected path
        is_protected = any(path.startswith(protected_path) for protected_path in self.PROTECTED_PATHS)
        
        if is_protected:
            # Check if user is authenticated and has CMS access
            if not request.user.is_authenticated:
                logger.warning(f"Unauthenticated access attempt to {path} from IP: {get_client_ip(request)}")
                return self._redirect_to_cms_login(request)
            
            # Check if user has CMS access
            try:
                cms_user = request.user.cms_user
                if not cms_user.has_api_access():
                    logger.warning(f"User {request.user.email} denied CMS access to {path}")
                    return self._access_denied_response(request)
                
                # Update CMS session activity
                self._update_cms_session(request, cms_user)
                
            except Exception as e:
                logger.error(f"Error checking CMS access for {request.user.email}: {str(e)}")
                return self._redirect_to_cms_login(request)
        
        return None
    
    def _redirect_to_cms_login(self, request):
        """Redirect to CMS login page."""
        # For API requests, return JSON response
        if request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'message': 'CMS authentication required',
                'errors': {'authentication': 'Please login to access this resource'},
                'login_url': '/cms/login/'
            }, status=401)
        
        # For web requests, redirect to login page
        return HttpResponseRedirect('/cms/login/')
    
    def _access_denied_response(self, request):
        """Return access denied response."""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'message': 'Access denied',
                'errors': {'authorization': 'You do not have permission to access this resource'}
            }, status=403)
        
        return JsonResponse({
            'success': False,
            'message': 'Access denied',
            'errors': {'authorization': 'You do not have permission to access this resource'}
        }, status=403)
    
    def _update_cms_session(self, request, cms_user):
        """Update CMS session activity."""
        try:
            session_key = request.session.session_key
            if session_key:
                from django.utils import timezone
                from authentication.models import CMSSession
                
                CMSSession.objects.filter(
                    cms_user=cms_user,
                    session_key=session_key,
                    is_active=True
                ).update(last_activity=timezone.now())
        except Exception as e:
            logger.error(f"Error updating CMS session: {str(e)}")


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

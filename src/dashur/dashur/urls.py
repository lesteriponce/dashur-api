"""
URL configuration for dashur project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def api_root(request):
    """API root endpoint showing available endpoints"""
    return JsonResponse({
        'message': 'Dashur API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'careers': '/api/careers/',
            'contacts': '/api/contacts/',
            'admin_careers': '/api/admin/careers/',
            'documentation': {
                'swagger': '/api/docs/',
                'redoc': '/api/redoc/',
                'schema': '/api/schema/'
            }
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # CMS web interface
    path('cms/', include(('cms_auth.urls', 'cms_auth'), namespace='cms_auth')),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # API endpoints (JWT Authentication)
    path('api/auth/', include('authentication.urls')),
    path('api/careers/', include('careers.urls')),
    path('api/contacts/', include('contacts.urls')),
    
    # Admin endpoints (SessionAuthentication for file uploads)
    path('api/admin/careers/', include('careers.admin_urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

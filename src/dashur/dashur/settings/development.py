"""
Development settings for the Dashur API project.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver']

# Database for development (SQLite for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Default email settings for contact forms
DEFAULT_FROM_EMAIL = 'noreply@dashur.com'
ADMIN_EMAIL = 'admin@dashur.com'

# Security settings for development (relaxed)
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'DENY'

# Debug toolbar (optional)
try:
    import debug_toolbar
    # Only enable debug toolbar if not in testing
    import sys
    if 'test' not in sys.argv:
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: True,
            'RESULTS_CACHE_SIZE': 100,
        }
        print("Debug toolbar: ENABLED")
    else:
        print("Debug toolbar: DISABLED (testing)")
except ImportError:
    print("Debug toolbar: DISABLED (debug_toolbar not installed)")
    # Optional: Install with: pip install django-debug-toolbar

# Logging for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['dashur']['level'] = 'DEBUG'

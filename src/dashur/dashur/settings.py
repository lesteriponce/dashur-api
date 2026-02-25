"""
Django settings for dashur project.

Environment-based configuration for development and production.
"""
import os
from decouple import config

ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .settings.production import *
elif ENVIRONMENT == 'development':
    from .settings.development import *
else:
    from .settings.base import *

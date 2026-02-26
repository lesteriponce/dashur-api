#!/usr/bin/env python
"""
Create demo admin user for testing.
"""
import os
import sys
import django
import logging
import argparse
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashur.settings.development')
django.setup()

from dashur.utils import create_admin_user

def create_demo_admin(
    email: Optional[str] = None, 
    password: Optional[str] = None, 
    first_name: Optional[str] = None, 
    last_name: Optional[str] = None, 
    is_super_admin: bool = False
) -> bool:
    """Create demo admin user."""
    # Use environment variables as defaults, then fall back to command line args, then defaults
    email = email or os.getenv('ADMIN_EMAIL', 'admin@example.com')
    password = password or os.getenv('ADMIN_PASSWORD', 'admin123')
    first_name = first_name or os.getenv('ADMIN_FIRST_NAME', 'Admin')
    last_name = last_name or os.getenv('ADMIN_LAST_NAME', 'User')
    is_super_admin = is_super_admin or os.getenv('ADMIN_IS_SUPER_ADMIN', 'false').lower() == 'true'
    
    try:
        admin_user = create_admin_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_super_admin=is_super_admin
        )
        logger.info("Admin user created successfully")
        logger.info(f"Email: {email}")
        logger.info(f"Name: {admin_user.full_name}")
        logger.info(f"Super Admin: {admin_user.is_super_admin}")
        return True
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create admin user for Dashur API')
    parser.add_argument('--email', help='Admin email address')
    parser.add_argument('--password', help='Admin password')
    parser.add_argument('--first-name', help='Admin first name')
    parser.add_argument('--last-name', help='Admin last name')
    parser.add_argument('--super-admin', action='store_true', help='Create as super admin')
    
    args = parser.parse_args()
    
    logger.info("Starting admin user creation...")
    success = create_demo_admin(
        email=args.email,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name,
        is_super_admin=args.super_admin
    )
    if success:
        logger.info("Admin user setup completed successfully")
    else:
        logger.error("Admin user creation failed")
        sys.exit(1)

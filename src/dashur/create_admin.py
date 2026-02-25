#!/usr/bin/env python
"""
Create demo admin user for testing.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashur.settings.development')
django.setup()

from dashur.utils import create_admin_user

def create_demo_admin():
    """Create demo admin user."""
    try:
        admin_user = create_admin_user(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_super_admin=True
        )
        print(f" Demo admin user created successfully!")
        print(f"   Email: admin@example.com")
        print(f"   Password: admin123")
        print(f"   Name: {admin_user.full_name}")
        print(f"   Super Admin: {admin_user.is_super_admin}")
        return True
    except Exception as e:
        print(f" Error creating admin user: {str(e)}")
        return False

if __name__ == '__main__':
    print("Creating demo admin user...")
    success = create_demo_admin()
    if success:
        print("\n Admin user setup complete!")
    else:
        print("\n Failed to create admin user")
        sys.exit(1)

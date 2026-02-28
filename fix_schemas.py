#!/usr/bin/env python3
"""
Script to add DRF Spectacular schema decorators to API views
"""
import re
import os

def fix_authentication_views():
    """Fix authentication views with schema decorators"""
    file_path = "src/dashur/authentication/views.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Schema mappings for different views
    schema_mappings = {
        'login': {
            'decorator': '@extend_schema(request=UserLoginSerializer, responses={200: UserSerializer}, description="Login user")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.AllowAny\]\)\s*def login\(request\):'
        },
        'logout': {
            'decorator': '@extend_schema(request=None, responses={200: dict}, description="Logout user")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def logout\(request\):'
        },
        'profile': {
            'decorator': '@extend_schema(responses={200: UserProfileSerializer}, description="Get user profile")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def profile\(request\):'
        },
        'update_profile': {
            'decorator': '@extend_schema(request=UserProfileUpdateSerializer, responses={200: UserProfileSerializer}, description="Update user profile")',
            'pattern': r'@api_view\(\[\'PUT\', \'PATCH\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def update_profile\(request\):'
        },
        'user_info': {
            'decorator': '@extend_schema(responses={200: UserSerializer}, description="Get current user info")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def user_info\(request\):'
        },
        'cms_login': {
            'decorator': '@extend_schema(request=CMSLoginSerializer, responses={200: CMSUserSerializer}, description="CMS login")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.AllowAny\]\)\s*def cms_login\(request\):'
        },
        'cms_logout': {
            'decorator': '@extend_schema(responses={200: dict}, description="CMS logout")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def cms_logout\(request\):'
        },
        'cms_profile': {
            'decorator': '@extend_schema(responses={200: CMSUserSerializer}, description="CMS profile")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def cms_profile\(request\):'
        },
        'cms_sessions': {
            'decorator': '@extend_schema(responses={200: CMSSessionSerializer}, description="CMS sessions")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def cms_sessions\(request\):'
        },
        'cms_revoke_session': {
            'decorator': '@extend_schema(responses={200: dict}, description="Revoke CMS session")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def cms_revoke_session\(request\):'
        }
    }
    
    # Apply schema decorators
    for view_name, mapping in schema_mappings.items():
        pattern = mapping['pattern']
        decorator = mapping['decorator']
        
        # Replace the pattern with decorator + pattern
        new_pattern = f"{decorator}\n    {pattern}"
        content = re.sub(pattern, new_pattern, content)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def fix_careers_views():
    """Fix careers views with schema decorators"""
    file_path = "src/dashur/careers/views.py"
    
    if not os.path.exists(file_path):
        return
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import if not present
    if 'from drf_spectacular.utils import extend_schema' not in content:
        content = content.replace(
            'from rest_framework import status, permissions',
            'from drf_spectacular.utils import extend_schema\nfrom rest_framework import status, permissions'
        )
    
    # Schema mappings
    schema_mappings = {
        'application_stats': {
            'decorator': '@extend_schema(responses={200: dict}, description="Get application stats")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def application_stats\(request\):'
        },
        'dashboard_stats': {
            'decorator': '@extend_schema(responses={200: dict}, description="Get dashboard stats")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def dashboard_stats\(request\):'
        },
        'my_applications': {
            'decorator': '@extend_schema(responses={200: dict}, description="Get my applications")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def my_applications\(request\):'
        },
        'recent_activity': {
            'decorator': '@extend_schema(responses={200: dict}, description="Get recent activity")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def recent_activity\(request\):'
        }
    }
    
    # Apply schema decorators
    for view_name, mapping in schema_mappings.items():
        pattern = mapping['pattern']
        decorator = mapping['decorator']
        
        # Replace the pattern with decorator + pattern
        new_pattern = f"{decorator}\n    {pattern}"
        content = re.sub(pattern, new_pattern, content)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def fix_contacts_views():
    """Fix contacts views with schema decorators"""
    file_path = "src/dashur/contacts/views.py"
    
    if not os.path.exists(file_path):
        return
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import if not present
    if 'from drf_spectacular.utils import extend_schema' not in content:
        content = content.replace(
            'from rest_framework import status, permissions',
            'from drf_spectacular.utils import extend_schema\nfrom rest_framework import status, permissions'
        )
    
    # Schema mappings
    schema_mappings = {
        'contact_stats': {
            'decorator': '@extend_schema(responses={200: dict}, description="Get contact stats")',
            'pattern': r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[permissions\.IsAuthenticated\]\)\s*def contact_stats\(request\):'
        },
        'create_contact_submission': {
            'decorator': '@extend_schema(responses={201: dict}, description="Create contact submission")',
            'pattern': r'@api_view\(\[\'POST\'\]\)\s*@permission_classes\(\[permissions\.AllowAny\]\)\s*def create_contact_submission\(request\):'
        }
    }
    
    # Apply schema decorators
    for view_name, mapping in schema_mappings.items():
        pattern = mapping['pattern']
        decorator = mapping['decorator']
        
        # Replace the pattern with decorator + pattern
        new_pattern = f"{decorator}\n    {pattern}"
        content = re.sub(pattern, new_pattern, content)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    os.chdir("/home/lesteriann/dashur-api")
    fix_authentication_views()
    fix_careers_views()
    fix_contacts_views()
    print("All schema decorators added!")

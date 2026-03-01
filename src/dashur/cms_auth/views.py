"""
CMS views for web interface.
"""
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from dashur.utils import get_client_ip

logger = logging.getLogger('dashur')


@csrf_protect
@require_http_methods(["GET", "POST"])
def cms_login_view(request):
    """
    CMS login view for web interface.
    """
    # Redirect if already authenticated and has CMS access
    if request.user.is_authenticated:
        try:
            cms_user = request.user.cms_user
            if cms_user.has_api_access():
                return redirect('cms_auth:cms_dashboard')
        except Exception:
            pass
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            
            if user and user.is_active:
                try:
                    cms_user = user.cms_user
                    if cms_user.has_api_access():
                        login(request, user)
                        
                        # Create CMS session record
                        from authentication.models import CMSSession
                        session_key = request.session.session_key
                        if session_key:
                            CMSSession.objects.update_or_create(
                                cms_user=cms_user,
                                session_key=session_key,
                                defaults={
                                    'ip_address': get_client_ip(request),
                                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                                    'is_active': True
                                }
                            )
                        
                        logger.info(f"CMS web login: {user.email} from IP: {get_client_ip(request)}")
                        messages.success(request, 'Login successful!')
                        return redirect('cms_auth:cms_dashboard')
                    else:
                        messages.error(request, 'CMS access denied. Please contact administrator.')
                except Exception as e:
                    logger.error(f"Error checking CMS access: {str(e)}")
                    messages.error(request, 'CMS user not found. Please contact administrator.')
            else:
                messages.error(request, 'Invalid credentials or account disabled.')
        else:
            messages.error(request, 'Please provide both email and password.')
    
    return render(request, 'cms/login.html')


@login_required
def cms_dashboard_view(request):
    """
    CMS dashboard view.
    """
    try:
        cms_user = request.user.cms_user
        if not cms_user.has_api_access():
            messages.error(request, 'Access denied')
            return redirect('cms_auth:cms_login')
        
        context = {
            'cms_user': cms_user,
            'user': request.user,
        }
        return render(request, 'cms/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading CMS dashboard: {str(e)}")
        messages.error(request, 'Error loading dashboard')
        return redirect('cms_auth:cms_login')


@login_required
def cms_profile_view(request):
    """
    CMS profile view.
    """
    try:
        cms_user = request.user.cms_user
        if not cms_user.has_api_access():
            messages.error(request, 'Access denied')
            return redirect('cms_auth:cms_login')
        
        # Get active sessions
        from authentication.models import CMSSession
        sessions = CMSSession.objects.filter(
            cms_user=cms_user,
            is_active=True
        ).order_by('-last_activity')
        
        context = {
            'cms_user': cms_user,
            'user': request.user,
            'sessions': sessions,
        }
        return render(request, 'cms/profile.html', context)
        
    except Exception as e:
        logger.error(f"Error loading CMS profile: {str(e)}")
        messages.error(request, 'Error loading profile')
        return redirect('cms_auth:cms_dashboard')


@login_required
@require_http_methods(["POST"])
def cms_logout_view(request):
    """
    CMS logout view for web interface.
    """
    try:
        # Deactivate CMS session
        from authentication.models import CMSSession
        session_key = request.session.session_key
        if session_key:
            CMSSession.objects.filter(
                cms_user__user=request.user,
                session_key=session_key,
                is_active=True
            ).update(is_active=False)
        
        logout(request)
        logger.info(f"CMS web logout: {request.user.email}")
        messages.success(request, 'Logged out successfully!')
        
    except Exception as e:
        logger.error(f"CMS logout error: {str(e)}")
        messages.error(request, 'Error during logout')
    
    return redirect('cms_auth:cms_login')


@login_required
@require_http_methods(["POST"])
def cms_revoke_session_view(request, session_key):
    """
    Revoke a specific CMS session.
    """
    try:
        cms_user = request.user.cms_user
        
        # Don't allow revoking current session
        current_session_key = request.session.session_key
        if session_key == current_session_key:
            messages.error(request, 'Cannot revoke current session')
            return redirect('cms_auth:cms_profile')
        
        # Revoke the session
        from authentication.models import CMSSession
        revoked_count = CMSSession.objects.filter(
            cms_user=cms_user,
            session_key=session_key,
            is_active=True
        ).update(is_active=False)
        
        if revoked_count > 0:
            messages.success(request, 'Session revoked successfully')
            logger.info(f"CMS session revoked: {session_key} by {request.user.email}")
        else:
            messages.error(request, 'Session not found or already revoked')
        
    except Exception as e:
        logger.error(f"CMS session revocation error: {str(e)}")
        messages.error(request, 'Error revoking session')
    
    return redirect('cms_auth:cms_profile')


def cms_access_denied_view(request):
    """
    Custom access denied view for CMS.
    """
    return render(request, 'cms/access_denied.html', status=403)

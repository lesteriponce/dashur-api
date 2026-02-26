"""
API views for the careers app.
"""
import logging
from rest_framework import status, permissions, generics, filters
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from dashur.utils import api_response
from dashur.utils_views import FileUploadAPIView  # Import custom view for file uploads
from .models import JobPosition, JobApplication, ApplicationStatusHistory
from .serializers import (
    JobPositionSerializer, JobPositionCreateSerializer, JobPositionListSerializer,
    JobApplicationSerializer, JobApplicationCreateSerializer, 
    JobApplicationUpdateSerializer, JobApplicationDetailSerializer,
    ApplicationStatusHistorySerializer
)

logger = logging.getLogger('dashur')


class JobPositionListCreateView(generics.ListCreateAPIView):
    """
    List and create job positions.
    """
    queryset = JobPosition.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_type', 'status', 'remote_work']
    search_fields = ['title', 'department', 'description']
    ordering_fields = ['created_at', 'title', 'salary_min']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobPositionCreateSerializer
        return JobPositionListSerializer
    
    def get_queryset(self):
        queryset = JobPosition.objects.all()
        
        # Filter by status for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='active')
        
        # Filter featured positions
        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Get the default paginated response structure
            response = self.get_paginated_response(serializer.data)
            
            # Extract pagination data and wrap with our API response format
            return api_response(
                success=True,
                data={
                    'count': response.data['count'],
                    'next': response.data['next'],
                    'previous': response.data['previous'],
                    'results': response.data['results']
                },
                message="Job positions retrieved successfully"
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Job positions retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return api_response(
                success=False,
                message="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save()
            logger.info(f"Job position created: {position.title} by {request.user.email}")
            
            response_serializer = JobPositionSerializer(position)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Job position created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return api_response(
            success=False,
            message="Job position creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class JobPositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete job positions.
    """
    queryset = JobPosition.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobPositionCreateSerializer
        return JobPositionSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            data=serializer.data,
            message="Job position retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return api_response(
                success=False,
                message="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            position = serializer.save()
            logger.info(f"Job position updated: {position.title} by {request.user.email}")
            
            response_serializer = JobPositionSerializer(position)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Job position updated successfully"
            )
        
        return api_response(
            success=False,
            message="Job position update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return api_response(
                success=False,
                message="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        title = instance.title
        instance.delete()
        logger.info(f"Job position deleted: {title} by {request.user.email}")
        
        return api_response(
            success=True,
            message="Job position deleted successfully"
        )


class JobApplicationListCreateView(generics.ListCreateAPIView):
    """
    List and create job applications.
    Supports both JWT and Session authentication for flexibility.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'position']
    search_fields = ['first_name', 'last_name', 'email', 'position__title']
    ordering_fields = ['applied_at', 'status']
    ordering = ['-applied_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobApplicationCreateSerializer
        return JobApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Non-staff users can only see their own applications
        if not user.is_staff:
            return JobApplication.objects.filter(user=user)
        
        # Staff can see all applications
        return JobApplication.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Get the default paginated response structure
            response = self.get_paginated_response(serializer.data)
            
            # Extract pagination data and wrap with our API response format
            return api_response(
                success=True,
                data={
                    'count': response.data['count'],
                    'next': response.data['next'],
                    'previous': response.data['previous'],
                    'results': response.data['results']
                },
                message="Job applications retrieved successfully"
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Job applications retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            application = serializer.save()
            logger.info(f"Job application submitted: {application.full_name} for {application.position.title}")
            
            response_serializer = JobApplicationSerializer(application)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Job application submitted successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return api_response(
            success=False,
            message="Job application submission failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class JobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve and update job applications.
    Supports both JWT and Session authentication.
    """
    queryset = JobApplication.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobApplicationUpdateSerializer
        return JobApplicationDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Non-staff users can only see their own applications
        if not user.is_staff:
            return JobApplication.objects.filter(user=user)
        
        # Staff can see all applications
        return JobApplication.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            data=serializer.data,
            message="Job application retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            application = serializer.save()
            logger.info(f"Job application updated: {application.full_name}")
            
            response_serializer = JobApplicationDetailSerializer(application)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Job application updated successfully"
            )
        
        return api_response(
            success=False,
            message="Job application update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = f"{instance.full_name} - {instance.position.title}"
        instance.delete()
        logger.info(f"Job application deleted: {title}")
        
        return api_response(
            success=True,
            message="Job application deleted successfully"
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_applications(request):
    """
    Get current user's job applications.
    """
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_at')
    serializer = JobApplicationSerializer(applications, many=True)
    
    return api_response(
        success=True,
        data=serializer.data,
        message="Your applications retrieved successfully"
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for admin panel.
    """
    if not request.user.is_staff:
        return api_response(
            success=False,
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Position statistics
        total_positions = JobPosition.objects.count()
        active_positions = JobPosition.objects.filter(status='active').count()
        
        # Application statistics
        total_applications = JobApplication.objects.count()
        pending_applications = JobApplication.objects.filter(status='pending').count()
        reviewed_applications = JobApplication.objects.filter(status='reviewed').count()
        accepted_applications = JobApplication.objects.filter(status='accepted').count()
        rejected_applications = JobApplication.objects.filter(status='rejected').count()
        
        # Recent activity (last 7 days)
        from django.utils import timezone
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        
        recent_applications = JobApplication.objects.filter(applied_at__gte=seven_days_ago).count()
        recent_positions = JobPosition.objects.filter(created_at__gte=seven_days_ago).count()
        
        stats = {
            'total_positions': total_positions,
            'active_positions': active_positions,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'reviewed_applications': reviewed_applications,
            'accepted_applications': accepted_applications,
            'rejected_applications': rejected_applications,
            'recent_applications': recent_applications,
            'recent_positions': recent_positions,
        }
        
        return api_response(
            success=True,
            data=stats,
            message="Dashboard statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to retrieve dashboard statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_activity(request):
    """
    Get recent activity for admin dashboard.
    """
    if not request.user.is_staff:
        return api_response(
            success=False,
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        activities = []
        
        # Recent applications
        recent_applications = JobApplication.objects.select_related('position').order_by('-applied_at')[:10]
        for app in recent_applications:
            activities.append({
                'type': 'application',
                'message': f"New application for {app.position.title}",
                'time': f"{timezone.now() - app.applied_at}".split(',')[0] + " ago",
                'timestamp': app.applied_at.isoformat()
            })
        
        # Recent position changes
        recent_positions = JobPosition.objects.order_by('-updated_at')[:5]
        for position in recent_positions:
            activities.append({
                'type': 'position',
                'message': f"Position {'created' if position.created_at == position.updated_at else 'updated'}: {position.title}",
                'time': f"{timezone.now() - position.updated_at}".split(',')[0] + " ago",
                'timestamp': position.updated_at.isoformat()
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return api_response(
            success=True,
            data={'recent_activity': activities[:20]},  # Return top 20
            message="Recent activity retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Recent activity error: {str(e)}")
        return api_response(
            success=False,
            message="Failed to retrieve recent activity",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def application_stats(request):
    """
    Get application statistics (staff only).
    """
    if not request.user.is_staff:
        return api_response(
            success=False,
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    total_applications = JobApplication.objects.count()
    pending_applications = JobApplication.objects.filter(status='pending').count()
    reviewed_applications = JobApplication.objects.filter(status='reviewed').count()
    accepted_applications = JobApplication.objects.filter(status='accepted').count()
    rejected_applications = JobApplication.objects.filter(status='rejected').count()
    
    stats = {
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'reviewed_applications': reviewed_applications,
        'accepted_applications': accepted_applications,
        'rejected_applications': rejected_applications,
        'active_positions': JobPosition.objects.filter(status='active').count(),
        'total_positions': JobPosition.objects.count(),
    }
    
    return api_response(
        success=True,
        data=stats,
        message="Application statistics retrieved successfully"
    )

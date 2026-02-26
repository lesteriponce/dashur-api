"""
API views for the contacts app.
"""
import logging
from rest_framework import status, permissions, generics, filters
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from dashur.utils import api_response
from .models import ContactSubmission, ContactResponse
from .serializers import (
    ContactSubmissionSerializer, ContactSubmissionCreateSerializer,
    ContactSubmissionUpdateSerializer, ContactSubmissionDetailSerializer,
    ContactSubmissionListSerializer, ContactResponseSerializer,
    ContactResponseCreateSerializer
)

logger = logging.getLogger('dashur')


def send_admin_notification(submission):
    """Send email notification to admin about new submission."""
    subject = f"New Contact Form Submission: {submission.subject}"
    message = f"""
    New contact form submission received:
    
    Name: {submission.full_name}
    Email: {submission.email}
    Phone: {submission.phone or 'Not provided'}
    Subject: {submission.subject}
    Message: {submission.message}
    Priority: {submission.get_priority_display()}
    
    ---
    This is an automated message from your Dashur API contact form.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Admin notification sent for: {submission.subject}")
    except Exception as e:
        logger.error(f"Failed to send admin notification email: {str(e)}")


class ContactSubmissionListView(generics.ListAPIView):
    """
    List contact submissions.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'newsletter_subscription']
    search_fields = ['first_name', 'last_name', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        return ContactSubmissionListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Non-staff users can only see their own submissions
        if not user.is_staff and user.is_authenticated:
            return ContactSubmission.objects.filter(email=user.email)
        
        # Staff can see all submissions
        return ContactSubmission.objects.all()
    
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
                message="Contact submissions retrieved successfully"
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Contact submissions retrieved successfully"
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_contact_submission(request):
    """
    Create a contact submission.
    Allows anonymous users to submit contact forms.
    """
    serializer = ContactSubmissionCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        submission = serializer.save()
        logger.info(f"Contact form submitted: {submission.full_name} - {submission.subject}")
        
        # Send notification email to admin
        try:
            send_admin_notification(submission)
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
        
        response_serializer = ContactSubmissionSerializer(submission)
        return api_response(
            success=True,
            data=response_serializer.data,
            message="Contact form submitted successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    return api_response(
        success=False,
        message="Contact form submission failed",
        errors=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


class ContactSubmissionDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update contact submissions.
    """
    queryset = ContactSubmission.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContactSubmissionUpdateSerializer
        return ContactSubmissionDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Non-staff users can only see their own submissions
        if not user.is_staff:
            return ContactSubmission.objects.filter(email=user.email)
        
        # Staff can see all submissions
        return ContactSubmission.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            data=serializer.data,
            message="Contact submission retrieved successfully"
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
            submission = serializer.save()
            logger.info(f"Contact submission updated: {submission.full_name} by {request.user.email}")
            
            response_serializer = ContactSubmissionDetailSerializer(submission)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Contact submission updated successfully"
            )
        
        return api_response(
            success=False,
            message="Contact submission update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ContactResponseListCreateView(generics.ListCreateAPIView):
    """
    List and create contact responses.
    """
    queryset = ContactResponse.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['response_email_sent', 'submission__status']
    search_fields = ['response_message', 'submission__subject', 'submission__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactResponseCreateSerializer
        return ContactResponseSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Non-staff users can only see responses to their own submissions
        if not user.is_staff:
            return ContactResponse.objects.filter(submission__email=user.email)
        
        # Staff can see all responses
        return ContactResponse.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                api_response(
                    success=True,
                    data=serializer.data,
                    message="Contact responses retrieved successfully"
                ).data
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Contact responses retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return api_response(
                success=False,
                message="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            response = serializer.save()
            logger.info(f"Contact response sent: {response.submission.full_name}")
            
            # Send response email to submitter
            try:
                self.send_response_email(response)
                response.response_email_sent = True
                response.save()
            except Exception as e:
                logger.error(f"Failed to send response email: {str(e)}")
            
            response_serializer = ContactResponseSerializer(response)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Contact response created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return api_response(
            success=False,
            message="Contact response creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def send_response_email(self, response):
        """Send response email to the contact submitter."""
        submission = response.submission
        subject = f"Re: {submission.subject}"
        message = f"""
        Dear {submission.full_name},
        
        Thank you for contacting us. We have received your message and our team will get back to you soon.
        
        Your original message:
        Subject: {submission.subject}
        {submission.message}
        
        Our response:
        {response.response_message}
        
        Best regards,
        The Dashur Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@dashur.com'),
            recipient_list=[submission.email],
            fail_silently=False,
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def contact_stats(request):
    """
    Get contact submission statistics (staff only).
    """
    if not request.user.is_staff:
        return api_response(
            success=False,
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    total_submissions = ContactSubmission.objects.count()
    new_submissions = ContactSubmission.objects.filter(status='new').count()
    read_submissions = ContactSubmission.objects.filter(status='read').count()
    responded_submissions = ContactSubmission.objects.filter(status='responded').count()
    
    urgent_submissions = ContactSubmission.objects.filter(priority='urgent').count()
    high_priority = ContactSubmission.objects.filter(priority='high').count()
    
    stats = {
        'total_submissions': total_submissions,
        'new_submissions': new_submissions,
        'read_submissions': read_submissions,
        'responded_submissions': responded_submissions,
        'urgent_submissions': urgent_submissions,
        'high_priority': high_priority,
        'total_responses': ContactResponse.objects.count(),
    }
    
    return api_response(
        success=True,
        data=stats,
        message="Contact statistics retrieved successfully"
    )

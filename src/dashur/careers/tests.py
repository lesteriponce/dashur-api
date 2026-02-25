"""
Tests for the careers app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import JobPosition, JobApplication

User = get_user_model()


class JobPositionModelTest(TestCase):
    """Test the JobPosition model."""
    
    def test_create_job_position(self):
        """Test creating a job position."""
        position = JobPosition.objects.create(
            title='Software Developer',
            department='Engineering',
            employment_type='full_time',
            description='Test job description',
            salary_min=50000,
            salary_max=80000
        )
        
        self.assertEqual(position.title, 'Software Developer')
        self.assertEqual(position.department, 'Engineering')
        self.assertTrue(position.is_active)
        self.assertEqual(str(position), 'Software Developer - Engineering')
    
    def test_salary_range_property(self):
        """Test the salary_range property."""
        position = JobPosition.objects.create(
            title='Software Developer',
            department='Engineering',
            employment_type='full_time',
            description='Test job description',
            salary_min=50000,
            salary_max=80000
        )
        
        self.assertEqual(position.get_salary_range(), '$50,000 - $80,000')


class JobApplicationModelTest(TestCase):
    """Test the JobApplication model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.position = JobPosition.objects.create(
            title='Software Developer',
            department='Engineering',
            employment_type='full_time',
            description='Test job description'
        )
    
    def test_create_job_application(self):
        """Test creating a job application."""
        application = JobApplication.objects.create(
            user=self.user,
            position=self.position,
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        self.assertEqual(application.user, self.user)
        self.assertEqual(application.position, self.position)
        self.assertTrue(application.is_pending)
        self.assertEqual(str(application), 'Test User - Software Developer')


class CareersAPITest(APITestCase):
    """Test the careers API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            first_name='Staff',
            last_name='User',
            password='staffpass123',
            is_staff=True
        )
        
        self.position = JobPosition.objects.create(
            title='Software Developer',
            department='Engineering',
            employment_type='full_time',
            description='Test job description',
            salary_min=50000,
            salary_max=80000
        )
    
    def test_list_job_positions(self):
        """Test listing job positions."""
        url = reverse('careers:position_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
    
    def test_create_job_position_staff(self):
        """Test creating a job position (staff only)."""
        self.client.force_authenticate(user=self.staff_user)
        
        position_data = {
            'title': 'Frontend Developer',
            'department': 'Engineering',
            'employment_type': 'full_time',
            'description': 'Test frontend job description',
            'salary_min': 60000,
            'salary_max': 90000
        }
        
        url = reverse('careers:position_list_create')
        response = self.client.post(url, position_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify position was created
        position = JobPosition.objects.get(title='Frontend Developer')
        self.assertEqual(position.department, 'Engineering')
    
    def test_create_job_position_unauthorized(self):
        """Test creating a job position without staff permissions."""
        self.client.force_authenticate(user=self.user)
        
        position_data = {
            'title': 'Frontend Developer',
            'department': 'Engineering',
            'employment_type': 'full_time',
            'description': 'Test frontend job description'
        }
        
        url = reverse('careers:position_list_create')
        response = self.client.post(url, position_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    def test_get_job_position_detail(self):
        """Test getting job position details."""
        url = reverse('careers:position_detail', kwargs={'pk': self.position.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], 'Software Developer')
    
    def test_submit_job_application(self):
        """Test submitting a job application."""
        self.client.force_authenticate(user=self.user)
        
        # Create a test resume file
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        application_data = {
            'position': self.position.pk,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'resume': resume,
            'cover_letter': 'Test cover letter'
        }
        
        url = reverse('careers:application_list_create')
        response = self.client.post(url, application_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify application was created
        application = JobApplication.objects.get(user=self.user, position=self.position)
        self.assertEqual(application.email, 'test@example.com')
    
    def test_submit_duplicate_application(self):
        """Test submitting duplicate application for same position."""
        # Create first application
        JobApplication.objects.create(
            user=self.user,
            position=self.position,
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        self.client.force_authenticate(user=self.user)
        
        application_data = {
            'position': self.position.pk,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
        
        url = reverse('careers:application_list_create')
        response = self.client.post(url, application_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_my_applications(self):
        """Test getting current user's applications."""
        # Create application
        JobApplication.objects.create(
            user=self.user,
            position=self.position,
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('careers:my_applications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
    
    def test_application_stats_staff(self):
        """Test getting application statistics (staff only)."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('careers:application_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('total_applications', response.data['data'])
    
    def test_application_stats_unauthorized(self):
        """Test getting application statistics without staff permissions."""
        self.client.force_authenticate(user=self.user)
        url = reverse('careers:application_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])

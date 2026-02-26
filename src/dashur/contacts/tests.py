"""
Tests for the contacts app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import ContactSubmission, ContactResponse

User = get_user_model()


class ContactSubmissionModelTest(TestCase):
    """Test the ContactSubmission model."""
    
    def test_create_contact_submission(self):
        """Test creating a contact submission."""
        submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            subject='Test Subject',
            message='Test message content',
            priority='medium'
        )
        
        self.assertEqual(submission.first_name, 'John')
        self.assertEqual(submission.last_name, 'Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertTrue(submission.is_new)
        self.assertEqual(str(submission), 'John Doe - Test Subject')


class ContactResponseModelTest(TestCase):
    """Test the ContactResponse model."""
    
    def setUp(self):
        """Set up test data."""
        self.submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        self.user = User.objects.create_user(
            email='staff@example.com',
            first_name='Staff',
            last_name='User',
            password='staffpass123',
            is_staff=True
        )
    
    def test_create_contact_response(self):
        """Test creating a contact response."""
        response = ContactResponse.objects.create(
            submission=self.submission,
            responded_by=self.user,
            response_message='Thank you for your message.'
        )
        
        self.assertEqual(response.submission, self.submission)
        self.assertEqual(response.responded_by, self.user)
        self.assertEqual(str(response), 'Response to John Doe')


class ContactsAPITest(APITestCase):
    """Test the contacts API endpoints."""
    
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
    
    def test_create_contact_submission(self):
        """Test creating a contact submission."""
        submission_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'subject': 'Test Subject',
            'message': 'This is a test message with sufficient length.',
            'priority': 'medium'
        }
        
        url = reverse('contacts:submission_create')
        response = self.client.post(url, submission_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify submission was created
        submission = ContactSubmission.objects.get(email='john@example.com')
        self.assertEqual(submission.first_name, 'John')
        self.assertEqual(submission.status, 'new')
    
    def test_create_contact_submission_short_message(self):
        """Test creating contact submission with short message."""
        submission_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Short',  # Too short
            'priority': 'medium'
        }
        
        url = reverse('contacts:submission_create')
        response = self.client.post(url, submission_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_list_contact_submissions_anonymous(self):
        """Test listing contact submissions as anonymous user."""
        url = reverse('contacts:submission_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Handle both paginated and non-paginated responses
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            submissions = data['results']
        else:
            submissions = data if isinstance(data, list) else []
        
        # Anonymous users should see empty list
        self.assertEqual(len(submissions), 0)
    
    def test_list_contact_submissions_user(self):
        """Test listing contact submissions as regular user."""
        # Create submissions
        ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='test@example.com',  # Same as user
            subject='Test Subject',
            message='Test message content'
        )
        
        ContactSubmission.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',  # Different from user
            subject='Another Subject',
            message='Another message content'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('contacts:submission_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Handle both paginated and non-paginated responses
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            submissions = data['results']
        else:
            submissions = data if isinstance(data, list) else []
        
        # User should only see their own submissions
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0]['email'], 'test@example.com')
    
    def test_list_contact_submissions_staff(self):
        """Test listing contact submissions as staff user."""
        # Create submissions
        ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        ContactSubmission.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            subject='Another Subject',
            message='Another message content'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('contacts:submission_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Handle both paginated and non-paginated responses
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            submissions = data['results']
        else:
            submissions = data if isinstance(data, list) else []
        
        # Staff should see all submissions
        self.assertEqual(len(submissions), 2)
    
    def test_get_contact_submission_detail(self):
        """Test getting contact submission details."""
        submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='test@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('contacts:submission_detail', kwargs={'pk': submission.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'test@example.com')
    
    def test_update_contact_submission_staff(self):
        """Test updating contact submission (staff only)."""
        submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('contacts:submission_detail', kwargs={'pk': submission.pk})
        
        update_data = {
            'status': 'read',
            'notes': 'Reviewed by staff'
        }
        
        response = self.client.patch(url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify submission was updated
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'read')
        self.assertEqual(submission.notes, 'Reviewed by staff')
    
    def test_create_contact_response(self):
        """Test creating a contact response (staff only)."""
        submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('contacts:response_list_create')
        
        response_data = {
            'submission': submission.pk,
            'response_message': 'Thank you for contacting us. We will respond soon.'
        }
        
        response = self.client.post(url, response_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify response was created
        contact_response = ContactResponse.objects.get(submission=submission)
        self.assertEqual(contact_response.responded_by, self.staff_user)
    
    def test_create_duplicate_response(self):
        """Test creating duplicate response for same submission."""
        submission = ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        # Create first response
        ContactResponse.objects.create(
            submission=submission,
            responded_by=self.staff_user,
            response_message='First response'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('contacts:response_list_create')
        
        response_data = {
            'submission': submission.pk,
            'response_message': 'Second response'
        }
        
        response = self.client.post(url, response_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_contact_stats_staff(self):
        """Test getting contact statistics (staff only)."""
        # Create test data
        ContactSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message content',
            priority='urgent'
        )
        
        ContactSubmission.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            subject='Another Subject',
            message='Another message content',
            status='read'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('contacts:contact_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['total_submissions'], 2)
        self.assertEqual(response.data['data']['new_submissions'], 1)
        self.assertEqual(response.data['data']['urgent_submissions'], 1)
    
    def test_contact_stats_unauthorized(self):
        """Test getting contact statistics without staff permissions."""
        self.client.force_authenticate(user=self.user)
        url = reverse('contacts:contact_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])

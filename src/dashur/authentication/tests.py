"""
Tests for the authentication app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test the custom User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created when User is created."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)


class AuthenticationAPITest(APITestCase):
    """Test the authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('authentication:register')
        response = self.client.post(url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
        self.assertIn('user', response.data['data'])
        
        # Verify user was created
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.first_name, 'Test')
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch."""
        data = self.user_data.copy()
        data['password_confirm'] = 'different'
        
        url = reverse('authentication:register')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_user_login(self):
        """Test user login endpoint."""
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        url = reverse('authentication:login')
        response = self.client.post(url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        url = reverse('authentication:login')
        response = self.client.post(url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_get_user_profile(self):
        """Test getting user profile."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        url = reverse('authentication:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'test@example.com')
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        url = reverse('authentication:update_profile')
        
        update_data = {
            'bio': 'Test bio',
            'location': 'Test City'
        }
        
        response = self.client.patch(url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['bio'], 'Test bio')
    
    def test_change_password(self):
        """Test changing password."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        url = reverse('authentication:change_password')
        
        password_data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(url, password_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify password was changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpass123'))
    
    def test_change_password_wrong_current(self):
        """Test changing password with wrong current password."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        url = reverse('authentication:change_password')
        
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(url, password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

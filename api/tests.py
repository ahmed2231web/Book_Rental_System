from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, date
import uuid

from .models import Book, Rental

User = get_user_model()


class ModelTests(TestCase):
    """Test model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='admin'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            publication_date=date.today(),
            genre='fiction',
            description='A test book',
            total_copies=5,
            available_copies=5
        )
    
    def test_user_creation(self):
        """Test user model creation"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'user')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(str(self.user), 'Test User (test@example.com)')
    
    def test_book_creation(self):
        """Test book model creation"""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.available_copies, 5)
        self.assertEqual(str(self.book), 'Test Book by Test Author')
    
    def test_rental_creation(self):
        """Test rental model creation"""
        rental = Rental.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        self.assertEqual(rental.status, 'active')
        self.assertEqual(rental.user, self.user)
        self.assertEqual(rental.book, self.book)


class AuthenticationTests(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        url = reverse('api:register')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User registered successfully')
        # Registration should NOT return tokens
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
    
    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        url = reverse('api:login')
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_profile(self):
        """Test user profile retrieval"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        # Authenticate user
        self.client.force_authenticate(user=user)
        
        url = reverse('api:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class BookTests(APITestCase):
    """Test book endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='User',
            last_name='Test',
            password='userpass123'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='Test',
            password='adminpass123',
            role='admin'
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            publication_date=date.today(),
            genre='fiction',
            description='A test book',
            total_copies=5,
            available_copies=5
        )
        
        self.book_data = {
            'title': 'New Test Book',
            'author': 'New Author',
            'isbn': '9876543210987',
            'publication_date': '2023-01-01',
            'genre': 'science_fiction',
            'description': 'A new test book',
            'total_copies': 3,
            'available_copies': 3
        }
    
    def test_list_books_authenticated(self):
        """Test listing books as authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:book_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_books_unauthenticated(self):
        """Test listing books without authentication"""
        url = reverse('api:book_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_book_admin(self):
        """Test creating book as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('api:book_list_create')
        response = self.client.post(url, self.book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Test Book')
    
    def test_create_book_user(self):
        """Test creating book as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:book_list_create')
        response = self.client.post(url, self.book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_book_detail(self):
        """Test getting book details"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:book_detail', kwargs={'pk': self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')
    
    def test_search_books(self):
        """Test book search functionality"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:book_list_create') + '?search=Test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class RentalTests(APITestCase):
    """Test rental endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='User',
            last_name='Test',
            password='userpass123'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='Test',
            password='adminpass123',
            role='admin'
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            publication_date=date.today(),
            genre='fiction',
            description='A test book',
            total_copies=5,
            available_copies=5
        )
    
    def test_create_rental(self):
        """Test creating a rental"""
        self.client.force_authenticate(user=self.user)
        
        rental_data = {
            'book': str(self.book.pk),
            'rental_period_days': 14
        }
        
        url = reverse('api:rental_create')
        response = self.client.post(url, rental_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that book available copies decreased
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
    
    def test_list_user_rentals(self):
        """Test listing user's rentals"""
        # Create a rental
        rental = Rental.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:rental_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_return_book(self):
        """Test returning a book"""
        # Create a rental
        rental = Rental.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        # Decrease available copies (simulating rental creation)
        self.book.available_copies -= 1
        self.book.save()
        
        self.client.force_authenticate(user=self.user)
        
        return_data = {
            'rental_id': str(rental.pk)
        }
        
        url = reverse('api:return_book')
        response = self.client.post(url, return_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that rental status changed
        rental.refresh_from_db()
        self.assertEqual(rental.status, 'returned')
        
        # Check that book available copies increased
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 5)
    
    def test_prevent_duplicate_rental(self):
        """Test preventing duplicate active rentals"""
        # Create initial rental
        Rental.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        self.client.force_authenticate(user=self.user)
        
        rental_data = {
            'book': str(self.book.pk),
            'rental_period_days': 14
        }
        
        url = reverse('api:rental_create')
        response = self.client.post(url, rental_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PermissionTests(APITestCase):
    """Test permission systems"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='User',
            last_name='Test',
            password='userpass123'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='Test',
            password='adminpass123',
            role='admin'
        )
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        # Admin should have access
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Regular user should not have access
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_list_admin_only(self):
        """Test user list is admin only"""
        # Admin should have access
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Regular user should not have access
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

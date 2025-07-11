from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('mystery', 'Mystery'),
        ('science_fiction', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('self_help', 'Self Help'),
        ('business', 'Business'),
        ('technology', 'Technology'),
        ('education', 'Education'),
        ('children', 'Children'),
        ('young_adult', 'Young Adult'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, db_index=True)
    author = models.CharField(max_length=200, db_index=True)
    isbn = models.CharField(max_length=13, unique=True, db_index=True)
    publication_date = models.DateField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, db_index=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['title', 'author']),
            models.Index(fields=['genre', 'publication_date']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Rental(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rentals')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='rentals')
    rented_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rentals'
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
        unique_together = ['user', 'book', 'status']  # Prevent multiple active rentals of same book by same user
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.status})"
    
    def is_overdue(self):
        return self.status == 'active' and timezone.now() > self.due_date
    
    def save(self, *args, **kwargs):
        # Auto-update status if overdue
        if self.status == 'active' and timezone.now() > self.due_date:
            self.status = 'overdue'
        super().save(*args, **kwargs)

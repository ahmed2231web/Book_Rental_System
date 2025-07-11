import django_filters
from django.db import models
from .models import Book, Rental


class BookFilter(django_filters.FilterSet):
    """Filter for books with advanced search capabilities"""
    
    # Text search across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Genre filter
    genre = django_filters.ChoiceFilter(choices=Book.GENRE_CHOICES)
    
    # Author filter (case-insensitive partial match)
    author = django_filters.CharFilter(lookup_expr='icontains')
    
    # Title filter (case-insensitive partial match)
    title = django_filters.CharFilter(lookup_expr='icontains')
    
    # Publication year filter
    publication_year = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year')
    publication_year_gte = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year__gte')
    publication_year_lte = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year__lte')
    
    # Availability filter
    available_only = django_filters.BooleanFilter(method='filter_available_only')
    
    # ISBN filter
    isbn = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Book
        fields = ['genre', 'author', 'title', 'publication_year', 'available_only', 'isbn']
    
    def filter_search(self, queryset, name, value):
        """
        Filter books by searching across title, author, and description.
        """
        if value:
            return queryset.filter(
                models.Q(title__icontains=value) |
                models.Q(author__icontains=value) |
                models.Q(description__icontains=value) |
                models.Q(isbn__icontains=value)
            )
        return queryset
    
    def filter_available_only(self, queryset, name, value):
        """
        Filter to show only available books (available_copies > 0).
        """
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset


class RentalFilter(django_filters.FilterSet):
    """Filter for rentals"""
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=Rental.STATUS_CHOICES)
    
    # User filter (for admin use)
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    
    # Book filter
    book_title = django_filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    book_author = django_filters.CharFilter(field_name='book__author', lookup_expr='icontains')
    
    # Date filters
    rented_after = django_filters.DateTimeFilter(field_name='rented_at', lookup_expr='gte')
    rented_before = django_filters.DateTimeFilter(field_name='rented_at', lookup_expr='lte')
    due_after = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_before = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    
    # Overdue filter
    overdue_only = django_filters.BooleanFilter(method='filter_overdue_only')
    
    class Meta:
        model = Rental
        fields = ['status', 'user_email', 'book_title', 'book_author', 'overdue_only']
    
    def filter_overdue_only(self, queryset, name, value):
        """
        Filter to show only overdue rentals.
        """
        if value:
            return queryset.filter(status='overdue')
        return queryset 
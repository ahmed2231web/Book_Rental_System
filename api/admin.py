from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book, Rental


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'publication_date', 'created_at')
    list_filter = ('genre', 'publication_date', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publication_date', 'genre')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'book_title', 'book_author', 'status', 'rented_at', 'due_date', 'returned_at', 'is_overdue')
    list_filter = ('status', 'rented_at', 'due_date', 'returned_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'book__title', 'book__author')
    ordering = ('-rented_at',)
    readonly_fields = ('id', 'rented_at', 'created_at', 'updated_at', 'is_overdue')
    
    fieldsets = (
        ('Rental Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('rented_at', 'due_date', 'returned_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book Title'
    book_title.admin_order_field = 'book__title'
    
    def book_author(self, obj):
        return obj.book.author
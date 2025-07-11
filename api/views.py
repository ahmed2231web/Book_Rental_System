from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import CustomUser, Book, Rental
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer, 
    UserProfileSerializer, UserUpdateSerializer, BookSerializer, 
    BookCreateUpdateSerializer, RentalSerializer, RentalCreateSerializer,
    RentalReturnSerializer, BookSearchSerializer, UserRegistrationResponseSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrReadOnly, IsOwnerOrAdmin, 
    CanManageBooks, CanManageRentals, IsAdminOrOwner
)
from .filters import BookFilter, RentalFilter


# Authentication Views
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that uses email instead of username
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="User Login",
        description="Login with email and password to get JWT tokens",
        request=CustomTokenObtainPairSerializer,
        responses={200: CustomTokenObtainPairSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User Registration",
        description="Register a new user account",
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user info only - no tokens
        return Response({
            'user': UserRegistrationResponseSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer
    
    @extend_schema(
        summary="Get User Profile",
        description="Get the current user's profile information",
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User Profile",
        description="Update the current user's profile information",
        request=UserUpdateSerializer,
        responses={200: UserProfileSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Logout endpoint that blacklists the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="User Logout",
        description="Logout user by blacklisting the refresh token",
        request={
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string'}
            }
        },
        responses={200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        }}
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "message": "Successfully logged out"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Invalid refresh token"
            }, status=status.HTTP_400_BAD_REQUEST)


# User Management Views (Admin only)
class UserListView(generics.ListAPIView):
    """
    List all users (Admin only)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_name']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="List Users",
        description="Get a list of all users (Admin only)",
        responses={200: UserProfileSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific user (Admin only)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Get User Details",
        description="Get details of a specific user (Admin only)",
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Book Views
class BookListCreateView(generics.ListCreateAPIView):
    """
    List books with search/filtering or create a new book
    """
    queryset = Book.objects.all()
    permission_classes = [CanManageBooks]
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['title', 'author', 'publication_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookCreateUpdateSerializer
        return BookSerializer
    
    @extend_schema(
        summary="List Books",
        description="Get a list of books with optional search and filtering",
        parameters=[
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search in title, author, description'),
            OpenApiParameter(name='genre', type=OpenApiTypes.STR, description='Filter by genre'),
            OpenApiParameter(name='author', type=OpenApiTypes.STR, description='Filter by author'),
            OpenApiParameter(name='available_only', type=OpenApiTypes.BOOL, description='Show only available books'),
            OpenApiParameter(name='publication_year', type=OpenApiTypes.INT, description='Filter by publication year'),
        ],
        responses={200: BookSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Book",
        description="Create a new book (Admin only)",
        request=BookCreateUpdateSerializer,
        responses={201: BookSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific book
    """
    queryset = Book.objects.all()
    permission_classes = [CanManageBooks]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookCreateUpdateSerializer
        return BookSerializer
    
    @extend_schema(
        summary="Get Book Details",
        description="Get details of a specific book",
        responses={200: BookSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Book",
        description="Update a specific book (Admin only)",
        request=BookCreateUpdateSerializer,
        responses={200: BookSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Book",
        description="Delete a specific book (Admin only)",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# Rental Views
class RentalListView(generics.ListAPIView):
    """
    List rentals - users see their own, admins see all
    """
    serializer_class = RentalSerializer
    permission_classes = [CanManageRentals]
    filterset_class = RentalFilter
    ordering_fields = ['rented_at', 'due_date', 'returned_at']
    ordering = ['-rented_at']
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Rental.objects.none()
        
        if self.request.user.role == 'admin':
            return Rental.objects.all().select_related('user', 'book')
        return Rental.objects.filter(user=self.request.user).select_related('book')
    
    @extend_schema(
        summary="List Rentals",
        description="List rentals - users see their own, admins see all",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by rental status'),
            OpenApiParameter(name='overdue_only', type=OpenApiTypes.BOOL, description='Show only overdue rentals'),
            OpenApiParameter(name='book_title', type=OpenApiTypes.STR, description='Filter by book title'),
        ],
        responses={200: RentalSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RentalCreateView(generics.CreateAPIView):
    """
    Create a new rental (rent a book)
    """
    serializer_class = RentalCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Rent a Book",
        description="Create a new rental for a book",
        request=RentalCreateSerializer,
        responses={201: RentalSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.save()
        return Response(
            RentalSerializer(rental).data,
            status=status.HTTP_201_CREATED
        )


class RentalDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific rental
    """
    serializer_class = RentalSerializer
    permission_classes = [CanManageRentals]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Rental.objects.none()
        
        if self.request.user.role == 'admin':
            return Rental.objects.all().select_related('user', 'book')
        return Rental.objects.filter(user=self.request.user).select_related('book')
    
    @extend_schema(
        summary="Get Rental Details",
        description="Get details of a specific rental",
        responses={200: RentalSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ReturnBookView(APIView):
    """
    Return a rented book
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Return Book",
        description="Return a rented book",
        request=RentalReturnSerializer,
        responses={200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'rental': {'type': 'object'}
            }
        }}
    )
    def post(self, request):
        serializer = RentalReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rental_id = serializer.validated_data['rental_id']
        
        try:
            # Get the rental
            if request.user.role == 'admin':
                rental = Rental.objects.get(id=rental_id)
            else:
                rental = Rental.objects.get(id=rental_id, user=request.user)
            
            if rental.status == 'returned':
                return Response({
                    'error': 'This book has already been returned'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update rental
            rental.status = 'returned'
            rental.returned_at = timezone.now()
            rental.save()
            
            # Increase available copies
            book = rental.book
            book.available_copies += 1
            book.save()
            
            return Response({
                'message': 'Book returned successfully',
                'rental': RentalSerializer(rental).data
            }, status=status.HTTP_200_OK)
            
        except Rental.DoesNotExist:
            return Response({
                'error': 'Rental not found or you do not have permission to return this book'
            }, status=status.HTTP_404_NOT_FOUND)


# Dashboard/Statistics Views
class DashboardStatsView(APIView):
    """
    Get dashboard statistics (Admin only)
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Dashboard Statistics",
        description="Get dashboard statistics for admins",
        responses={200: {
            'type': 'object',
            'properties': {
                'total_books': {'type': 'integer'},
                'total_users': {'type': 'integer'},
                'active_rentals': {'type': 'integer'},
                'overdue_rentals': {'type': 'integer'},
                'available_books': {'type': 'integer'},
            }
        }}
    )
    def get(self, request):
        stats = {
            'total_books': Book.objects.count(),
            'total_users': CustomUser.objects.filter(role='user').count(),
            'active_rentals': Rental.objects.filter(status='active').count(),
            'overdue_rentals': Rental.objects.filter(status='overdue').count(),
            'available_books': Book.objects.filter(available_copies__gt=0).count(),
            'total_available_copies': sum(Book.objects.values_list('available_copies', flat=True)),
        }
        return Response(stats)


class MyRentalsView(generics.ListAPIView):
    """
    Get current user's rentals
    """
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = RentalFilter
    ordering = ['-rented_at']
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Rental.objects.none()
        
        return Rental.objects.filter(user=self.request.user).select_related('book')
    
    @extend_schema(
        summary="My Rentals",
        description="Get current user's rental history",
        responses={200: RentalSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Health Check
class HealthCheckView(APIView):
    """
    Simple health check endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Health Check",
        description="Simple health check endpoint",
        responses={200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'timestamp': {'type': 'string', 'format': 'date-time'}
            }
        }}
    )
    def get(self, request):
        return Response({
            'message': 'Book Rental System API is running',
            'timestamp': timezone.now()
        })


# Keep the function-based view as an alias
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@extend_schema(
    summary="Health Check",
    description="Simple health check endpoint",
    responses={200: {'message': 'string'}}
)
def health_check(request):
    """
    Simple health check endpoint
    """
    return Response({
        'message': 'Book Rental System API is running',
        'timestamp': timezone.now()
    })

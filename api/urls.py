from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Health check
    path('', views.health_check, name='health_check'),
    
    # Authentication endpoints
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    
    # User management endpoints (Admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Book endpoints
    path('books/', views.BookListCreateView.as_view(), name='book_list_create'),
    path('books/<uuid:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    
    # Rental endpoints
    path('rentals/', views.RentalListView.as_view(), name='rental_list'),
    path('rentals/create/', views.RentalCreateView.as_view(), name='rental_create'),
    path('rentals/<uuid:pk>/', views.RentalDetailView.as_view(), name='rental_detail'),
    path('rentals/return/', views.ReturnBookView.as_view(), name='return_book'),
    path('rentals/my/', views.MyRentalsView.as_view(), name='my_rentals'),
    
    # Dashboard and statistics (Admin only)
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
] 
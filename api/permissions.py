from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users to access.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admin users full access, and read-only access for others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners to access their own objects, or admin users to access any.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == 'admin':
            return True
        
        # Check if the object has a user field and if it belongs to the requesting user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For user profile objects
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission to allow admin users full access, or users to access their own data.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == 'admin':
            return True
        
        # Users can only access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For user profile objects
        return obj == request.user


class CanManageBooks(permissions.BasePermission):
    """
    Permission to allow admin users to create, update, and delete books.
    Regular users can only view books.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class CanManageRentals(permissions.BasePermission):
    """
    Permission to allow users to rent books and manage their own rentals.
    Admin users can view all rentals.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any rental
        if request.user.role == 'admin':
            return True
        
        # Users can only access their own rentals
        return obj.user == request.user 
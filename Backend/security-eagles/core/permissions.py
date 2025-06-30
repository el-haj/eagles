# accounts/permissions.py

from rest_framework import permissions

class IsAdminOrReadOwn(permissions.BasePermission):
    """
    Custom permission to only allow admins to access all user data,
    - Admins have full access.
    - Users can only GET their own data.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_staff:
                return True  
            if view.action in ['retrieve']:
                return True  
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True  
        if view.action == 'retrieve':
            return obj == request.user 
        return False



from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to GET (read),
    Only admins can POST, PUT, DELETE (write).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

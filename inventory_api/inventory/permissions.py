from rest_framework import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """Only the creator of an item can edit or delete it but anyone can read it"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by == request.user
    
class IsAdminOrReadOnly(BasePermission):
    """Only admin user/staff  can create , update or delete .Anyone can read"""    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
    
class IsSelfOrAdmin(BasePermission):
    """Users can only edit their own account, admins can edit any account"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_staff
         
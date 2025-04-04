from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.created_by == request.user

class IsGameSessionOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a game session to view or modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner
        return obj.user == request.user

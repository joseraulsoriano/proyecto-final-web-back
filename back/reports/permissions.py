from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Permiso para moderadores (Admin/Profesor)"""
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role in ['ADMIN', 'PROFESSOR']
        return False



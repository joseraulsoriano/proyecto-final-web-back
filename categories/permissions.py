from rest_framework import permissions


class IsAdminOrProfessor(permissions.BasePermission):
    """Permiso para Admin o Profesor"""
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role in ['ADMIN', 'PROFESSOR']
        return False



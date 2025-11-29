from rest_framework import permissions


class IsAuthorOrModerator(permissions.BasePermission):
    """Permiso para autor o moderador (Admin/Profesor)"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # El autor puede editar/eliminar
        if obj.author == request.user:
            return True
        
        # Admin y Profesor pueden editar/eliminar cualquier post
        if request.user.role in ['ADMIN', 'PROFESSOR']:
            return True
        
        return False



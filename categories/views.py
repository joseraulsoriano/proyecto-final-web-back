from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from .models import Category
from .serializers import CategorySerializer
from .permissions import IsAdminOrProfessor


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.annotate(
        posts_count_annotated=Count('posts', filter=Q(posts__status='PUBLISHED'))
    )
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # Permitir acceso público a list y retrieve
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Solo Admin/Profesor pueden crear, actualizar o eliminar
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle_status', 'archive', 'restore']:
            return [IsAdminOrProfessor()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # Por defecto, excluir categorías archivadas en list (solo para usuarios no admin)
            user = self.request.user
            if not user.is_authenticated or user.role not in ['ADMIN', 'PROFESSOR']:
                queryset = queryset.exclude(status='ARCHIVED')
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """Cambiar estado activo/inactivo"""
        category = self.get_object()
        if category.status == 'ACTIVE':
            # Verificar si tiene posts publicados
            if category.posts.filter(status='PUBLISHED').exists():
                return Response(
                    {'error': 'No se puede desactivar una categoría con posts publicados'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.status = 'INACTIVE'
        else:
            category.status = 'ACTIVE'
        category.save()
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def archive(self, request, pk=None):
        """Archivar una categoría (ocultarla del frontend sin eliminarla)"""
        category = self.get_object()
        category.status = 'ARCHIVED'
        category.save()
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None):
        """Restaurar una categoría archivada"""
        category = self.get_object()
        if category.status == 'ARCHIVED':
            category.status = 'ACTIVE'
            category.save()
            serializer = CategorySerializer(category, context={'request': request})
            return Response(serializer.data)
        return Response(
            {'error': 'Solo se pueden restaurar categorías archivadas'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """Sobrescribir para validar que no tenga posts. Si tiene posts, sugerir usar estado inactivo."""
        category = self.get_object()
        if category.posts.exists():
            posts_count = category.posts.count()
            return Response(
                {
                    'error': f'No se puede eliminar una categoría que tiene {posts_count} post(s) asociado(s)',
                    'suggestion': 'En su lugar, cambia el estado de la categoría a INACTIVE para ocultarla sin eliminarla',
                    'has_posts': True,
                    'posts_count': posts_count
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

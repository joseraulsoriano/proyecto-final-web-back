from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Tag
from .serializers import PostSerializer, TagSerializer
from .permissions import IsAuthorOrModerator


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    # Por defecto, permitir acceso público (se sobrescribe en get_permissions para acciones protegidas)
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        # Permitir acceso público para listar y ver posts publicados
        action = getattr(self, 'action', None)
        if action in ['list', 'retrieve']:
            return [AllowAny()]
        # Para actualizar/eliminar, verificar autor o moderador
        if action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorOrModerator()]
        # Para otras acciones (create, publish, archive, etc), requiere autenticación
        return [IsAuthenticated()]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author', 'category').prefetch_related('tags').annotate(
            comments_count_annotated=Count('comments')
        )
        
        # Filtro por categoría
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filtro por estado (por defecto solo publicados para usuarios normales o no autenticados)
        status_filter = self.request.query_params.get('status')
        user = self.request.user
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        elif not user.is_authenticated or user.role not in ['ADMIN', 'PROFESSOR']:
            # Usuarios no autenticados o estudiantes solo ven posts publicados
            queryset = queryset.filter(status='PUBLISHED')
        
        # Filtro por búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='my-posts')
    def my_posts(self, request):
        """Obtener posts del usuario autenticado"""
        posts = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='publish')
    def publish(self, request, pk=None):
        """Publicar un post"""
        post = self.get_object()
        if post.author != request.user and request.user.role not in ['ADMIN', 'PROFESSOR']:
            return Response(
                {'error': 'No tienes permisos para publicar este post'},
                status=status.HTTP_403_FORBIDDEN
            )
        post.status = 'PUBLISHED'
        post.save()
        return Response(PostSerializer(post).data)
    
    @action(detail=True, methods=['patch'], url_path='archive')
    def archive(self, request, pk=None):
        """Archivar un post"""
        post = self.get_object()
        if post.author != request.user and request.user.role not in ['ADMIN', 'PROFESSOR']:
            return Response(
                {'error': 'No tienes permisos para archivar este post'},
                status=status.HTTP_403_FORBIDDEN
            )
        post.status = 'ARCHIVED'
        post.save()
        return Response(PostSerializer(post).data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para etiquetas"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # Permitir acceso público para listar tags
        if self.action == 'list':
            from rest_framework.permissions import AllowAny
            return [AllowAny()]
        return super().get_permissions()

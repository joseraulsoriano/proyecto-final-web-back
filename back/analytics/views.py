from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from posts.models import Post
from categories.models import Category
from comments.models import Comment
from accounts.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics(request):
    """Estadísticas generales de la plataforma"""
    
    # Posts por categoría
    posts_by_category = Category.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='PUBLISHED'))
    ).values('id', 'name', 'posts_count').order_by('-posts_count')
    
    # Usuarios más activos (top posters)
    top_posters_raw = User.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='PUBLISHED'))
    ).filter(posts_count__gt=0).order_by('-posts_count')[:10]
    
    top_posters = []
    for user in top_posters_raw:
        top_posters.append({
            'id': user.id,
            'full_name': user.get_full_name(),
            'email': user.email,
            'posts_count': user.posts_count
        })
    
    # Categorías más comentadas
    categories_most_commented = Category.objects.annotate(
        comments_count=Count('posts__comments', filter=Q(posts__status='PUBLISHED'))
    ).filter(comments_count__gt=0).values(
        'id', 'name', 'comments_count'
    ).order_by('-comments_count')[:10]
    
    # Estadísticas generales
    total_posts = Post.objects.filter(status='PUBLISHED').count()
    total_comments = Comment.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    
    # Posts recientes (últimos 7 días)
    week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(
        status='PUBLISHED',
        created_at__gte=week_ago
    ).count()
    
    return Response({
        'general': {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_users': total_users,
            'recent_posts_week': recent_posts
        },
        'posts_by_category': list(posts_by_category),
        'top_posters': top_posters,
        'categories_most_commented': list(categories_most_commented)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_stats(request, category_id):
    """Estadísticas de una categoría específica"""
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Categoría no encontrada'}, status=404)
    
    posts = Post.objects.filter(category=category, status='PUBLISHED')
    total_posts = posts.count()
    total_comments = Comment.objects.filter(post__in=posts).count()
    
    # Posts más comentados de esta categoría
    top_posts = posts.annotate(
        comments_count=Count('comments')
    ).order_by('-comments_count')[:5].values(
        'id', 'title', 'comments_count', 'created_at'
    )
    
    return Response({
        'category': {
            'id': category.id,
            'name': category.name,
            'description': category.description
        },
        'stats': {
            'total_posts': total_posts,
            'total_comments': total_comments
        },
        'top_posts': list(top_posts)
    })

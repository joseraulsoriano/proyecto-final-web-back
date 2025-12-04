from rest_framework import serializers
from .models import Report
from accounts.serializers import UserSerializer
from posts.serializers import PostSerializer
from comments.serializers import CommentSerializer


class SimplePostSerializer(serializers.Serializer):
    """Serializer simplificado para posts en reportes"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()


class SimpleCommentSerializer(serializers.Serializer):
    """Serializer simplificado para comentarios en reportes"""
    id = serializers.IntegerField()
    content = serializers.CharField()
    author = UserSerializer(read_only=True)


class ReportSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    post = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = ['id', 'type', 'reported_by', 'post', 'comment',
                 'reason', 'status', 'reviewed_by', 'action_taken', 'created_at', 'reviewed_at']
        read_only_fields = ['reported_by', 'reviewed_by', 'reviewed_at', 'status', 'action_taken']
    
    def get_post(self, obj):
        """Serializar post solo si existe y no fue eliminado"""
        if not obj.post_id:
            return None
        
        # Verificar si el post existe antes de intentar serializarlo
        try:
            # Acceder al post de forma segura
            post = obj.post
            if post is None:
                return None
            return SimplePostSerializer(post).data
        except Exception as e:
            # Si el post fue eliminado o hay algún error, retornar None
            # Esto puede pasar si el post fue eliminado pero el reporte todavía existe
            # (aunque con CASCADE no debería pasar, pero por seguridad lo manejamos)
            return None
    
    def get_comment(self, obj):
        """Serializar comentario solo si existe y no fue eliminado"""
        if not obj.comment_id:
            return None
        
        try:
            # Acceder al comentario de forma segura
            comment = obj.comment
            if comment is None:
                return None
            # Usar serializer simplificado para evitar serialización anidada del post
            # NO serializar el post dentro del comentario para evitar problemas
            return {
                'id': comment.id,
                'content': comment.content,
                'author': UserSerializer(comment.author, context=self.context).data,
                'created_at': comment.created_at
            }
        except Exception as e:
            # Si el comentario fue eliminado o hay algún error, retornar None
            return None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from posts.models import Post
        from comments.models import Comment
        
        # Agregar post_id y comment_id como campos write-only
        self.fields['post_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Post.objects.all(),
            write_only=True,
            required=False,
            source='post'
        )
        self.fields['comment_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Comment.objects.all(),
            write_only=True,
            required=False,
            source='comment'
        )
    
    def validate(self, data):
        if data.get('type') == 'POST' and not data.get('post'):
            raise serializers.ValidationError({'post_id': 'La publicación es requerida para reportes de tipo POST'})
        if data.get('type') == 'COMMENT' and not data.get('comment'):
            raise serializers.ValidationError({'comment_id': 'El comentario es requerido para reportes de tipo COMMENT'})
        return data
    
    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


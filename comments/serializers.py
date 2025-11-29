from rest_framework import serializers
from django.core.validators import MinLengthValidator
from .models import Comment
from accounts.serializers import UserSerializer
from posts.serializers import PostSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'author', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from posts.models import Post
        
        # Agregar post_id como campo write-only
        # Permitir comentar en todos los posts (PUBLISHED, DRAFT, etc.)
        # La validación de permisos se hace en la vista
        self.fields['post_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Post.objects.all(),
            write_only=True,
            source='post',
            required=True
        )
    
    def get_author(self, obj):
        """Obtener el autor con el contexto del request para URLs absolutas"""
        request = self.context.get('request')
        return UserSerializer(obj.author, context={'request': request}).data
    
    def validate_content(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("El comentario debe tener al menos 5 caracteres")
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


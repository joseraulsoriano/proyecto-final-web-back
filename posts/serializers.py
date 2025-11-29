from rest_framework import serializers
from django.core.validators import MinLengthValidator
from .models import Post, Tag
from categories.serializers import CategorySerializer
from accounts.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'author', 'status', 
                 'tags', 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        # Usar el valor annotado si existe, sino usar la propiedad del modelo
        return getattr(obj, 'comments_count_annotated', getattr(obj, 'comments_count', obj.comments.count()))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from categories.models import Category
        
        # Agregar category_id como campo write-only
        self.fields['category_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.filter(status='ACTIVE'),
            write_only=True,
            source='category',
            required=True
        )
        
        # Agregar tag_ids como campo write-only
        self.fields['tag_ids'] = serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all(),
            many=True,
            write_only=True,
            source='tags',
            required=False
        )
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres")
        return value
    
    def validate_content(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("El contenido debe tener al menos 20 caracteres")
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if 'category' not in validated_data:
            raise serializers.ValidationError({'category_id': 'La categoría es obligatoria'})
        return super().create(validated_data)
    


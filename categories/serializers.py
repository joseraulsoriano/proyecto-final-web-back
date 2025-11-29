from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    
    def get_posts_count(self, obj):
        # Usar el valor annotado si existe, sino usar la propiedad del modelo
        return getattr(obj, 'posts_count_annotated', getattr(obj, 'posts_count', obj.posts.filter(status='PUBLISHED').count()))
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status', 'created_by', 
                 'created_at', 'updated_at', 'posts_count']
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'posts_count']
    
    def validate_name(self, value):
        # Verificar unicidad
        if self.instance:  # Si es actualización
            if Category.objects.filter(name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe una categoría con este nombre")
        else:  # Si es creación
            if Category.objects.filter(name=value).exists():
                raise serializers.ValidationError("Ya existe una categoría con este nombre")
        return value



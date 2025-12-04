from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_by', 'created_at', 'posts_count_display']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    
    def posts_count_display(self, obj):
        return obj.posts.count()
    posts_count_display.short_description = 'Posts'

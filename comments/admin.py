from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__email', 'post__title']
    readonly_fields = ['created_at', 'updated_at']

from rest_framework import serializers
from .models import Report
from accounts.serializers import UserSerializer
from posts.serializers import PostSerializer
from comments.serializers import CommentSerializer


class ReportSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'type', 'reported_by', 'post', 'comment',
                 'reason', 'status', 'reviewed_by', 'action_taken', 'created_at', 'reviewed_at']
        read_only_fields = ['reported_by', 'reviewed_by', 'reviewed_at', 'status', 'action_taken']
    
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


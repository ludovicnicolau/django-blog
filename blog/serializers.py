from rest_framework import serializers

from .models import BlogPost, Comment, Like

class BlogPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    author_username = serializers.SerializerMethodField()

    def get_author_username(self, obj):
        return obj.get_author_username_display

    class Meta:
        model = BlogPost
        fields = ('id', 'slug', 'title', 'content', 'last_edited_date', 'author_username', 'likes_count', 'is_published',)
        read_only_fields = ('id', 'slug', 'last_edited_date', 'author', 'likes_count',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'author', 'last_edited_date',)
        read_only_fields = ('author', 'last_edited_date',)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('blog_post', 'user',)
        read_only_fields = ('blog_post', 'user',)
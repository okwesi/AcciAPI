from rest_framework import serializers

from apps.content.models import Post
from apps.content.serializers.post import PostMediaSerializer, PostOwnerSerializer


class LikeSerializer(serializers.Serializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(is_active=True),
                                              write_only=True)


class ShareSerializer(serializers.Serializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(is_active=True),
                                              write_only=True)


class FavoriteSerializer(serializers.Serializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(is_active=True),
                                              write_only=True)

    def validate_post(self, post):
        if post.post_type != 'feed':
            raise serializers.ValidationError("Can only favorite a Post.")
        return post


class ListFavoritesSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    created_by = PostOwnerSerializer(read_only=True)
    liked = serializers.BooleanField()

    class Meta:
        model = Post
        fields = [
            'id', 'post_type', 'content',
            'comments', 'likes', 'media', 'liked',
            'date_created', 'created_by',
        ]

    def get_created_by(self, obj):
        return obj.created_by.get_full_name()

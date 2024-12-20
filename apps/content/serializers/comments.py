from rest_framework import serializers

from apps.content.models import Post
from apps.content.serializers.post import PostOwnerSerializer


class CommentSerializer(serializers.ModelSerializer):
    created_by = PostOwnerSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    parent = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Post
        fields = [
            'id', 'content', 'comments', 'likes',
            'date_created', 'created_by', 'replies',
            'parent'
        ]
        read_only_fields = ['comments', 'likes', 'date_created', 'created_by', 'replies']

    def get_created_by(self, obj):
        return obj.created_by.get_full_name()

    def get_replies(self, obj):
        queryset = obj.replies.filter(post_type='comment').order_by('-date_created')
        return CommentSerializer(queryset, many=True).data

    def validate_parent(self, value):
        try:
            parent = Post.objects.get(id=value, post_type__in=['feed', 'comment'], is_active=True)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Cannot comment on this Post")
        return parent

    def create(self, validated_data):
        validated_data['created_by'] = self.context['user']
        validated_data['post_type'] = 'comment'
        comment = Post.objects.create(**validated_data)
        parent = validated_data['parent']
        parent.add_comment_interaction(self.context['user'])
        parent.increment_comment_count()

        return comment

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ListCommentsSerializer(serializers.ModelSerializer):
    created_by = PostOwnerSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'content', 'comments', 'likes',
            'date_created', 'created_by', 'replies'
        ]

    def get_created_by(self, obj):
        return obj.created_by.get_full_name()

    def get_replies(self, obj):
        queryset = obj.replies.filter(post_type='comment', is_active=True).order_by('-date_created')
        return ListCommentsSerializer(queryset, many=True).data

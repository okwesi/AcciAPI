from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.content.models import Post, PostMedia
from apps.jurisdiction.serializers.branch import ShortBranchSerializer

User = get_user_model()


class PostOwnerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'avatar']

    def get_full_name(self, obj):
        return obj.get_full_name()


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'file_type', 'date_created']
        read_only_fields = ['id', 'date_created']


class PostSerializer(serializers.ModelSerializer):
    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    media = PostMediaSerializer(many=True, read_only=True)
    created_by = PostOwnerSerializer(read_only=True)
    branch = ShortBranchSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'post_type', 'content',
            'comments', 'likes',
            'media_files', 'media', 'date_created',
            'created_by', 'branch'
        ]
        read_only_fields = ['post_type', 'comments', 'likes', 'media', 'date_created', 'created_by', 'branch']

    def validate_media_files(self, media_files):
        allowed_file_types = [choice[0] for choice in PostMedia.FILE_TYPE_CHOICES]
        for media_file in media_files:
            file_type = media_file.content_type.split('/')[0]
            if file_type not in allowed_file_types:
                allowed_types_str = ', '.join(allowed_file_types)
                raise serializers.ValidationError(
                    f"Unsupported file type: {file_type}. Allowed types are: {allowed_types_str}.")
        return media_files

    def create(self, validated_data):
        validated_data['branch'] = self.context['user'].branch
        media_files_data = validated_data.pop('media_files', [])
        validated_data['created_by'] = self.context['user']
        validated_data['post_type'] = 'feed'
        post = Post.objects.create(**validated_data)

        for media_data in media_files_data:
            self.save_media(post, media_data)

        return post

    def update(self, instance, validated_data):
        media_files_data = validated_data.pop('media_files', None)

        instance = super().update(instance, validated_data)

        if media_files_data is not None:
            instance.media.all().delete()
            for media_data in media_files_data:
                self.save_media(instance, media_data)

        return instance

    def save_media(self, post, media_file):
        file_type = media_file.content_type.split('/')[0]
        PostMedia.objects.create(post=post, file=media_file, file_type=file_type)


class ListPostsSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    is_favorite = serializers.BooleanField()
    liked = serializers.BooleanField()
    created_by = PostOwnerSerializer(read_only=True)
    branch = ShortBranchSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'post_type', 'content',
            'comments', 'likes', 'shares', 'media', 'branch',
            'is_favorite', 'liked', 'date_created', 'created_by'
        ]

    def get_created_by(self, obj):
        return obj.created_by.get_full_name()


class AdminListPostsSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    created_by = PostOwnerSerializer(read_only=True)
    branch = ShortBranchSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'post_type', 'content',
            'comments', 'likes', 'shares', 'media', 'branch',
            'date_created', 'created_by'
        ]

    def get_created_by(self, obj):
        return obj.created_by.get_full_name()

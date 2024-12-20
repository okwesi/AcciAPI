from django.contrib.auth import get_user_model
from django.db import models

from apps.shared.models import BaseModel

User = get_user_model()


class Post(BaseModel):
    POST_TYPES_CHOICES = (
        ('feed', 'Feed Post'),
        ('slider', 'slider'),
        ('comment', 'Comment'),
    )
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPES_CHOICES
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    comments = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created']),
            models.Index(fields=['post_type']),
        ]

    def __str__(self):
        return f"{self.post_type} by {self.created_by} ({self.id})"

    def add_comment_interaction(self, user):
        """Creates a 'comment' interaction for the given user."""
        UserInteraction.objects.create(
            user=user,
            post=self,
            interaction_type='comment'
        )

    def increment_comment_count(self):
        self.comments = models.F('comments') + 1
        self.save(update_fields=['comments'])


class PostMedia(BaseModel):
    FILE_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media'
    )
    file = models.FileField(
        upload_to='post_media/'
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES
    )

    class Meta:
        ordering = ['date_created']
        verbose_name = 'Post Media'
        verbose_name_plural = 'Post Media'
        indexes = [
            models.Index(fields=['post', 'file_type']),
        ]

    def __str__(self):
        return f"{self.file_type} for post {self.post.id}"


class UserInteraction(BaseModel):
    INTERACTION_TYPE_CHOICES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('favorite', 'Favorite'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPE_CHOICES
    )

    class Meta:
        ordering = ['-date_created']
        # unique_together = ['user', 'post', 'interaction_type']
        indexes = [
            models.Index(fields=['user', 'post', 'interaction_type']),
            models.Index(fields=['post', 'interaction_type']),
        ]

    def __str__(self):
        return f"{self.interaction_type} by {self.user} on post {self.post.id}"

    def set_like(self, user, post):
        interaction, created = UserInteraction.objects.get_or_create(
            user=user,
            post=post,
            interaction_type='like'
        )
        if not created:
            interaction.delete()
            if post.likes > 0:
                post.likes = models.F('likes') - 1
        else:
            post.likes = models.F('likes') + 1
        post.save(update_fields=['likes'])
        return created

    def set_favorite(self, user, post):
        """Sets or unsets the favorite interaction for a given user and post."""
        interaction, created = UserInteraction.objects.get_or_create(
            user=user,
            post=post,
            interaction_type='favorite'
        )
        if not created:
            interaction.delete()
        return created

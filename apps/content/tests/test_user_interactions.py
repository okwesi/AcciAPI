import json

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factory import UserFactory
from apps.content.models import UserInteraction
from apps.content.tests.factories import PostFactory


@pytest.mark.django_db
class TestUserInteractionViewSet:
    def setup_method(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def _assign_permission(self, codename):
        permission = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(permission)
        self.user.save()

    # LIKE interaction tests
    def test_like_post_with_permission(self):
        post = PostFactory()
        url = reverse('user-interactions-like')
        payload = {'post': post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == 'Liked'
        post.refresh_from_db()
        assert post.likes == 1

    def test_unlike_post_with_permission(self):
        post = PostFactory(is_active=True, post_type='feed')
        UserInteraction.objects.create(user=self.user, post=post, interaction_type='like')
        url = reverse('user-interactions-like')
        payload = {'post': post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == 'Unliked'
        post.refresh_from_db()
        assert post.likes == 0

    # FAVORITE interaction tests
    def test_favorite_post_with_permission(self):
        post = PostFactory(post_type='feed')
        url = reverse('user-interactions-favorite')
        payload = {'post': post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == 'Added to Favorites'

    def test_unfavorite_post_with_permission(self):
        post = PostFactory(post_type="feed")
        UserInteraction.objects.create(user=self.user, post=post, interaction_type='favorite')
        url = reverse('user-interactions-favorite')
        payload = {'post': post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == 'Removed from Favorite'

    def test_favorite_non_feed_post_with_permission(self):
        post = PostFactory(post_type='comment')
        url = reverse('user-interactions-favorite')
        payload = {'post': post.id}

        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_favorites_with_permission(self):
        posts = PostFactory.create_batch(3, is_active=True, post_type='feed')
        for post in posts:
            UserInteraction.objects.create(user=self.user, post=post, interaction_type='favorite')

        url = reverse('user-interactions-list-favorites')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

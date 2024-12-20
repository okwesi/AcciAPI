import json

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factory import UserFactory
from apps.content.tests.factories import PostFactory


# pytest -v apps/content/tests/test_comments.py

@pytest.mark.django_db
class TestCommentViewSet:
    def setup_method(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def _assign_permission(self, codename):
        """Helper method to assign permission to user."""
        permission = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(permission)
        self.user.save()

    # CREATE Comment Tests


    def test_create_comment_with_permission(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        url = reverse('comment-list')
        payload = {'content': 'This is a comment', 'parent': parent_post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a comment'



    def test_update_comment_with_permission(self):
        comment = PostFactory(created_by=self.user, is_active=True, post_type='comment')
        url = reverse('comment-detail', args=[comment.id])
        payload = {'content': 'Updated content'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == 'Updated content'

    def test_update_nonexistent_comment(self):
        url = reverse('comment-detail', args=[99999])
        payload = {'content': 'Trying to update a nonexistent comment'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'message' in response.data

    # DELETE Comment Tests

    def test_delete_comment_with_permission(self):
        comment = PostFactory(created_by=self.user, is_active=True, post_type='comment')
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert not comment.is_active

    def test_delete_nonexistent_comment(self):
        url = reverse('comment-detail', args=[99999])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'message' in response.data

    # LIST Comment Tests
    def test_list_comments_with_permission(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        commnts = PostFactory.create_batch(3, parent=parent_post, post_type='comment', is_active=True)
        print(commnts)
        url = reverse('comment-list')
        response = self.client.get(url, {'page': 1, 'page_size': 3, 'parent': parent_post.id})
        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert len(response.data['results']) == 3


    def test_list_comments_with_pagination(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        PostFactory.create_batch(10, parent=parent_post, post_type='comment')
        url = reverse('comment-list')
        response = self.client.get(url, {'page': 2, 'page_size': 3, 'parent': parent_post.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        assert response.data['pagination']['page'] == 2

    def test_create_comment_with_empty_content(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        url = reverse('comment-list')
        payload = {'content': '', 'parent': parent_post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data

    def test_create_comment_on_inactive_parent_post(self):
        parent_post = PostFactory(is_active=False, post_type='feed')
        url = reverse('comment-list')
        payload = {'content': 'Comment on inactive post', 'parent': parent_post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'parent' in response.data

    def test_create_comment_on_invalid_post_type(self):
        parent_post = PostFactory(is_active=True, post_type='slider')
        url = reverse('comment-list')
        payload = {'content': 'Comment on invalid post type', 'parent': parent_post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'parent' in response.data

        # Edge Case: Attempt to update a deleted comment

    def test_update_deleted_comment(self):
        comment = PostFactory(created_by=self.user, is_active=False, post_type='comment')
        url = reverse('comment-detail', args=[comment.id])
        payload = {'content': 'Updating deleted comment'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'message' in response.data

    def test_list_comments_for_post_with_no_comments(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        url = reverse('comment-list')
        response = self.client.get(url, {'feed': parent_post.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    def test_list_comments_with_invalid_page_number(self):
        parent_post = PostFactory(is_active=True, post_type='feed')
        PostFactory.create_batch(5, parent=parent_post, post_type='comment')
        url = reverse('comment-list') + '?page=999&page_size=2'
        response = self.client.get(url, {'feed': parent_post.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    @pytest.mark.parametrize('content', ['Comment 1', 'Comment 2', 'Comment 3'])
    def test_rapid_comment_creation(self, content):
        parent_post = PostFactory(is_active=True, post_type='feed')
        url = reverse('comment-list')
        payload = {'content': content, 'parent': parent_post.id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS]

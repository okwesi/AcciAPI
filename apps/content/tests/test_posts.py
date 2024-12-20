import json

import pytest
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factory import UserFactory
from apps.content.models import Post, PostMedia
from apps.content.tests.factories import PostFactory, PostMediaFactory
from apps.shared.literals import CREATE_POST, DELETE_POST, UPDATE_POST


# pytest -v apps/content/tests/test_posts.py

@pytest.mark.django_db
class TestPostViewSet:
    def setup_method(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def _assign_permission(self, codename):
        """Helper method to assign permission to user."""
        # Fetch the specific permission
        permission = Permission.objects.get(codename=codename)
        # Add the permission to the user directly
        self.user.user_permissions.add(permission)
        self.user.save()

    def _create_test_file(self, file_type='image', filename='test.jpg'):
        """Helper method to create a test file."""
        return SimpleUploadedFile(filename, b'test content', content_type=f'{file_type}/jpeg')

    # CREATE Post Tests
    def test_create_post_without_permission(self):
        url = reverse('post-list')
        payload = {'content': 'Attempt to create post without permission'}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_post_with_single_image_file(self):
        self._assign_permission(CREATE_POST)
        url = reverse('post-list')
        payload = {
            'content': 'Post with a single image file',
            'media_files': [self._create_test_file()]
        }
        response = self.client.post(url, data=payload, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        post = Post.objects.get(content='Post with a single image file')
        assert post.media.count() == 1
        assert post.media.first().file_type == 'image'

    def test_create_post_with_multiple_media_files(self):
        self._assign_permission(CREATE_POST)
        url = reverse('post-list')
        payload = {
            'content': 'Post with multiple media files',
            'media_files': [self._create_test_file('image'), self._create_test_file('video', 'test.mp4')]
        }
        response = self.client.post(url, data=payload, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        post = Post.objects.get(content='Post with multiple media files')
        assert post.media.count() == 2
        assert set(post.media.values_list('file_type', flat=True)) == {'image', 'video'}

    def test_create_post_without_content(self):
        self._assign_permission(CREATE_POST)
        url = reverse('post-list')
        payload = {'content': '', 'media_files': [self._create_test_file()]}
        response = self.client.post(url, data=payload, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data

    # UPDATE Post Tests
    def test_update_post_without_permission(self):
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        url = reverse('post-detail', args=[post.id])
        payload = {'content': 'Partially updated content'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_post_replace_media_files(self):
        self._assign_permission(UPDATE_POST)
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        initial_media = PostMediaFactory(post=post, file_type='image')
        url = reverse('post-detail', args=[post.id])
        payload = {'media_files': [self._create_test_file('video', 'new_video.mp4')]}
        response = self.client.put(url, data=payload, format='multipart')
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.media.count() == 1
        assert post.media.first().file.name.endswith('new_video.mp4')
        assert not PostMedia.objects.filter(id=initial_media.id).exists()

    def test_partial_update_post_content(self):
        self._assign_permission(UPDATE_POST)
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        url = reverse('post-detail', args=[post.id])
        payload = {'content': 'Partially updated content'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.content == 'Partially updated content'

    # DELETE Post Tests
    def test_delete_post_without_permission(self):
        post = PostFactory(created_by=self.user)
        PostMediaFactory.create_batch(3, post=post)
        url = reverse('post-detail', args=[post.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_post_without_media_files(self):
        self._assign_permission(DELETE_POST)
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        url = reverse('post-detail', args=[post.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert not post.is_active

    def test_delete_post_with_media_files(self):
        self._assign_permission(DELETE_POST)
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        PostMediaFactory(post=post)
        url = reverse('post-detail', args=[post.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert not post.is_active
        assert PostMedia.objects.filter(post=post).exists()

    def test_delete_nonexistent_post(self):
        self._assign_permission(DELETE_POST)
        url = reverse('post-detail', args=[99999])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # LIST Post Tests
    def test_list_posts_with_permission(self):
        PostFactory.create_batch(3, is_active=True, post_type='feed')
        url = reverse('post-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_list_posts_with_pagination(self):
        PostFactory.create_batch(10, is_active=True, post_type='feed')
        url = reverse('post-list') + '?page=2&page_size=3'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        assert response.data['pagination']['page'] == 2

    def test_create_post_with_invalid_media_file_type(self):
        self._assign_permission(CREATE_POST)
        url = reverse('post-list')
        payload = {
            'content': 'Post with invalid media file type',
            'media_files': [self._create_test_file('application', 'invalid.pdf')]
        }
        response = self.client.post(url, data=payload, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'media_files' in response.data

    def test_delete_post_with_comments(self):
        self._assign_permission(DELETE_POST)
        post = PostFactory(created_by=self.user, is_active=True, post_type='feed')
        PostFactory.create_batch(3, parent=post, post_type='comment')
        url = reverse('post-detail', args=[post.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert not post.is_active
        assert Post.objects.filter(parent=post).exists()

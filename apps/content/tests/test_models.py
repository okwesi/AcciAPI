import pytest

from apps.accounts.tests.factory import UserFactory
from apps.content.models import UserInteraction
from apps.content.tests.factories import PostFactory, PostMediaFactory, UserInteractionFactory


@pytest.mark.django_db
def test_post_creation():
    post = PostFactory()
    assert post.comments == 0
    assert post.likes == 0
    assert post.post_type in ['feed', 'slider', 'comment']


@pytest.mark.django_db
def test_media_creation():
    media = PostMediaFactory()
    assert media.file_type in ['image', 'video', 'audio']
    assert media.file is not None


@pytest.mark.django_db
def test_user_interaction():
    user = UserFactory()
    post = PostFactory()
    interaction = UserInteractionFactory(user=user, post=post, interaction_type='like')
    assert interaction.interaction_type == 'like'
    assert interaction.user == user
    assert interaction.post == post


@pytest.mark.django_db
def test_set_like():
    user = UserFactory()
    post = PostFactory()
    interaction = UserInteraction(user=user, post=post, interaction_type='like')
    created = interaction.set_like(user, post)
    assert created is True
    post.refresh_from_db()
    assert post.likes == 1

    created = interaction.set_like(user, post)
    assert created is False
    post.refresh_from_db()
    assert post.likes == 0

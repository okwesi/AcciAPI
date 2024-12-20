import factory

from apps.accounts.tests.factory import UserFactory
from apps.content.models import Post, PostMedia, UserInteraction


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    created_by = factory.SubFactory(UserFactory)
    post_type = factory.Iterator(['feed', 'slider', 'comment'])
    content = factory.Faker("text")
    parent = None  # You can set this to another Post instance if testing nested comments.
    comments = 0
    likes = 0
    is_active=True


class PostMediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostMedia

    post = factory.SubFactory(PostFactory)
    file = factory.django.FileField(filename='test_image.jpg')
    file_type = factory.Iterator(['image', 'video', 'audio'])


class UserInteractionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserInteraction
        django_get_or_create = ('user', 'post', 'interaction_type')

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    interaction_type = factory.Iterator(['like', 'comment', 'favorite'])

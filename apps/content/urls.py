from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.content.views.comments import CommentViewSet
from apps.content.views.post import PostViewSet
from apps.content.views.user_interactions import UserInteractionViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'content/post', PostViewSet, basename='post')
router.register(r'content/comment', CommentViewSet, basename='comment')
router.register(r'content/user-interactions', UserInteractionViewSet, basename='user-interactions')

urlpatterns = [
    path('', include(router.urls)),
]

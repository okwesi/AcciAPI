from rest_framework import routers
from django.urls import path, include

from apps.member.views import MemberViewSet

router = routers.DefaultRouter()
router.register(r'members', MemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

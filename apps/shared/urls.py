from django.urls import path, include
from rest_framework import routers

from apps.shared.views.custom_types import CustomTypesViewSet

router = routers.DefaultRouter()
router.register(r'custom-types', CustomTypesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

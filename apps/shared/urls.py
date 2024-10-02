from django.urls import path, include
from rest_framework import routers

from apps.shared.views.custom_types import CustomTypesViewSet
from apps.shared.views.dashboard import DashboardViewSet

router = routers.DefaultRouter()
router.register(r'custom-types', CustomTypesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard', DashboardViewSet.as_view({'get': 'get_dashboard_data'}))
]

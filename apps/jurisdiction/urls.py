from rest_framework import routers
from django.urls import path, include

from apps.jurisdiction.views.area import AreaViewSet
from apps.jurisdiction.views.district import DistrictViewSet
from apps.jurisdiction.views.branch import BranchViewSet

router = routers.DefaultRouter()
router.register(r'jurisdiction/areas', AreaViewSet, basename='areas')
router.register(r'jurisdiction/districts', DistrictViewSet, basename='districts')
router.register(r'jurisdiction/branches', BranchViewSet, basename='branches')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.api.view.auth import UserAuthViewSet
from apps.accounts.api.view.users import PermissionListView, GroupsView, UserAccountViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'accounts/auth', UserAuthViewSet, basename='auth')
router.register(r'accounts/users/admin', UserAccountViewSet, basename='users')

urlpatterns = [
    path('accounts/users/permissions', PermissionListView.as_view(), name='permissions'),
    path('accounts/users/groups', GroupsView.as_view(
        {'get': 'list', 'post': 'create'}
    ), name='groups'),
    path('accounts/users/groups/<int:pk>', GroupsView.as_view(
        {'put': 'update', 'delete': 'destroy'}
    ),
         name='groups'
         ),

    path('accounts/users/auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import viewsets, status, views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q

from apps.accounts.api.serializers.auth import UserSerializer
from apps.accounts.api.serializers.users import NewUserSerializer, GroupSerializer, PermissionSerializer, \
    GroupWithRankSerializer
from apps.accounts.models import AppPermission, AppGroup
from apps.member.models import Member
from apps.shared.general import GENERAL_SUCCESS_RESPONSE
from apps.shared.literals import ADD_ADMIN, UPDATE_ADMIN, DELETE_ADMIN, LIST_ADMINS, VIEW_GROUPS_AND_ROLES, \
    CREATE_GROUPS_AND_ROLES, UPDATE_GROUPS_AND_ROLES, DELETE_GROUPS_AND_ROLES
from apps.shared.utils.permissions import UserPermission

User = get_user_model()


class UserAccountViewSet(viewsets.GenericViewSet):
    """
    A viewset for handling user account management: login, logout, change password, reset_password, update profile.
    """

    serializer_class = NewUserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        permissions = {
            'create': ADD_ADMIN,
            'update': UPDATE_ADMIN,
            'destroy': DELETE_ADMIN,
            'list': LIST_ADMINS,
            'retrieve': LIST_ADMINS
        }
        user_permission = permissions[self.action]
        print(f'user: {self.request.user}'
              f' permission to check:{user_permission}')
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                member, created = Member.objects.update_or_create(phone_number=user.phone_number,
                                                                  defaults={
                                                                      'first_name': user.first_name,
                                                                      'last_name': user.last_name,
                                                                      'email': user.email,
                                                                      'gender': user.gender,
                                                                      'branch': user.branch
                                                                  })
                user.member = member
                user.save()
            except Exception as e:
                pass
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing user.
        """

        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a user.
        """
        try:
            user = self.get_queryset().get(is_active=True, id=pk)
            fields_to_encrypt = ['email', 'phone_number', 'username']
            user.soft_delete(owner=request.user, fields_to_encrypt=fields_to_encrypt)
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """
        List all users.
        """
        query = request.query_params.get('query')
        queryset = self.get_queryset().filter(is_active=True)

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query) |
                Q(username__iexact=query)
            )

        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)
        serializer = UserSerializer(page_obj, many=True)

        return Response({
            'results': serializer.data,
            'pagination': {
                'total': queryset.count(),
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        """
        List all users.
        """
        try:
            user = self.get_queryset().filter(is_active=True).get(id=pk)
            serializer = UserSerializer(user)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupsView(viewsets.GenericViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.select_related('ranking')

    def get_permissions(self):
        permissions = {
            'create': CREATE_GROUPS_AND_ROLES,
            'update': UPDATE_GROUPS_AND_ROLES,
            'destroy': DELETE_GROUPS_AND_ROLES,
            'list': VIEW_GROUPS_AND_ROLES,
        }
        user_permission = permissions[self.action]
        print(f'user: {self.request.user}'
              f' permission to check:{user_permission}')
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def list(self, request, *args, **kwargs):
        groups = Group.objects.prefetch_related('permissions').filter(
            ranking__is_active=True
        ).order_by(
            'ranking__rank', 'name'
        )
        serializer = GroupSerializer(groups, many=True, context=dict(
            request=request
        ))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = GroupWithRankSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response(self.get_serializer(group).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = GroupWithRankSerializer(instance=group, data=request.data, partial=True)
        if serializer.is_valid():
            group = serializer.save()
            return Response(self.get_serializer(group).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request,pk, *args, **kwargs):
        try:
            group = AppGroup.objects.get_groups(is_active=True).get(
                id=pk
            )

            # Check if there are users assigned to the group
            if group.user_set.exists():
                raise ValidationError({
                    'error': 'Cannot delete a role with assigned users. '
                             'Please detach assigned users first'
                })

            # Check if the group is a default group
            if group.ranking.is_default:
                raise ValidationError({'error': "Default role cannot be deleted"})

            group.delete()
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except Group.DoesNotExist as e:
            raise ValidationError({'error': 'Role could not be found'})
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class PermissionListView(views.APIView):
    """
    Retrieve all custom permissions, excluding Django's default permissions.
    """

    def get_permissions(self):
        permissions = {
            'retrieve': VIEW_GROUPS_AND_ROLES,
            'list': VIEW_GROUPS_AND_ROLES,
        }
        user_permission = permissions['retrieve']
        print(f'user: {self.request.user}'
              f' permission to check:{user_permission}')
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def get(self, request, *args, **kwargs):
        # Fetch permissions our custom permissions. exlude the django default permissions
        permissions = AppPermission.objects.get_permissions()
        # Serialize and return the permissions
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

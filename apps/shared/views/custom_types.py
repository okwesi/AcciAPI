from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shared.literals import ADD_CUSTOM_TYPE, UPDATE_CUSTOM_TYPE, DELETE_CUSTOM_TYPE, VIEW_CUSTOM_TYPES
from apps.shared.models import CustomTypes
from apps.shared.serializers.custom_types import CustomTypesSerializer
from apps.shared.utils.permissions import UserPermission


class CustomTypesViewSet(viewsets.GenericViewSet):
    serializer_class = CustomTypesSerializer
    queryset = CustomTypes.objects.all()

    def get_permissions(self):
        permissions = {
            'create': ADD_CUSTOM_TYPE,
            'update': UPDATE_CUSTOM_TYPE,
            'destroy': DELETE_CUSTOM_TYPE,
            'list': VIEW_CUSTOM_TYPES,
        }
        user_permission = permissions[self.action]
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        serializer = CustomTypesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            custom_type = CustomTypes.objects.get(id=pk, is_active=True)
        except CustomTypes.DoesNotExist:
            return Response({'message': 'Custom Type not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomTypesSerializer(custom_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            custom_type.date_modified = datetime.now()
            custom_type.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            custom_type = CustomTypes.objects.get(id=pk, is_active=True)
            custom_type.soft_delete(owner=request.user)
            return Response({'message': 'Custom Type deleted successfully'}, status=status.HTTP_200_OK)
        except CustomTypes.DoesNotExist:
            return Response({'message': 'Custom Type not found'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        queryset = CustomTypes.objects.filter(is_active=True)
        serializer = CustomTypesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

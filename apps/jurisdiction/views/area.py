from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shared.literals import ADD_AREA, UPDATE_AREA, DELETE_AREA, VIEW_AREAS
from apps.shared.utils.permissions import UserPermission
from apps.jurisdiction.models import Area
from apps.jurisdiction.serializers.area import AreaSerializer, FullAreaSerializer


class AreaViewSet(viewsets.GenericViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()

    def get_permissions(self):
        permissions = {
            'create': ADD_AREA,
            'update': UPDATE_AREA,
            'destroy': DELETE_AREA,
            'list': VIEW_AREAS,
            'retrieve': VIEW_AREAS
        }
        user_permission = permissions[self.action]
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        """
        Create a new area

        Args:
            request: The request object containing the data to be created
            {"name": "Area Name", "area_head": 1}

        Returns:
            Response: The response object containing the created area data
            {"message": "Area created successfully", "data": {"name": "Area Name", "area_head": 1}}
        """
        request.data['created_by'] = request.user
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            area = serializer.save()
            return Response(FullAreaSerializer(area).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an area

        Args:
            request: The request object containing the data to be updated
            pk: The primary key of the area

        Returns:
            Response: The response object containing the updated area data
            {"message": "Area updated successfully", "data": {"name": "Area Name", "area_head": 1}}
        """
        try:
            area = Area.objects.get(id=pk, is_active=True)
        except Area.DoesNotExist:
            return Response({'message': 'Area not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AreaSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            updated_area = serializer.save()
            area.date_modified = datetime.now()
            area.modified_by = request.user
            area.save()
            return Response(FullAreaSerializer(updated_area).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Soft delete an area

        Args:
            request: The request object containing the data to be deleted
            pk: The primary key of the area

        Returns:
            Response: The response object containing the deleted area data
            {"message": "Area deleted successfully"}
        """
        try:
            area = self.get_queryset().get(id=pk, is_active=True)
            area.soft_delete(owner=request.user)
            return Response({'message': 'Area deleted successfully'}, status=status.HTTP_200_OK)
        except Area.DoesNotExist:
            return Response({'message': 'Area not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """
        Retrieve an area

        Args:
            request: The request object containing the data to be retrieved
            pk: The primary key of the area

        Returns:
            Response: The response object containing the retrieved area data
            {"message": "Area retrieved successfully", "data": {"name": "Area Name", "area_head": 1}}
        """
        try:
            # TODO: add branches, districts and their various details AND ADD THE PERMISSIONS
            area = Area.objects.get(id=pk, is_active=True)
        except Area.DoesNotExist:
            return Response({'message': 'Area not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullAreaSerializer(area)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        """
        List all areas

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of areas
        """
        query = request.query_params.get('query', None)
        queryset = self.get_queryset().filter(is_active=True).order_by('name')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = FullAreaSerializer(page_obj, many=True)
            results = {
                'results': serializer.data,
                'pagination': {
                    'total': queryset.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
        else:
            results = FullAreaSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)


# TODO: ADD VIEW YOUR OWN DISTRICT
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.jurisdiction.models import District
from apps.jurisdiction.serializers.district import DistrictSerializer, FullDistrictSerializer
from apps.shared.literals import ADD_DISTRICT, UPDATE_DISTRICT, DELETE_DISTRICT, VIEW_DISTRICTS
from apps.shared.utils.permissions import UserPermission


class DistrictViewSet(viewsets.GenericViewSet):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()

    def get_permissions(self):
        permissions = {
            'create': ADD_DISTRICT,
            'update': UPDATE_DISTRICT,
            'destroy': DELETE_DISTRICT,
            'list': VIEW_DISTRICTS,
            'retrieve': VIEW_DISTRICTS
        }
        user_permission = permissions[self.action]
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        """
        Create a new district

        Args:
            request: The request object containing the data to be created
            {"name": "District Name", "district_head": 1}

        Returns:
            Response: The response object containing the created district data
            {"message": "District created successfully", "data": {"name": "District Name", "district_head": 1}}
        """
        request.data['created_by'] = request.user.id
        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            district = serializer.save()
            return Response(FullDistrictSerializer(district).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update a district

        Args:
            request: The request object containing the data to be updated
            pk: The primary key of the district

        Returns:
            Response: The response object containing the updated district data
        """
        try:
            district = District.objects.get(id=pk, is_active=True)
        except District.DoesNotExist:
            return Response({'message': 'District not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DistrictSerializer(district, data=request.data, partial=True)
        if serializer.is_valid():
            updated_district = serializer.save()
            district.date_modified = datetime.now()
            district.modified_by = request.user
            district.save()
            return Response(FullDistrictSerializer(updated_district).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a district

        Args:
            request: The request object containing the data to be deleted
            pk: The primary key of the district

        Returns:
            Response: The response object containing the deleted district data
        """
        try:
            district = self.get_queryset().get(id=pk, is_active=True)
            district.soft_delete(owner=request.user)
            return Response({'message': 'District deleted successfully'}, status=status.HTTP_200_OK)
        except District.DoesNotExist:
            return Response({'message': 'District not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """
        Retrieve a district

        Args:
            request: The request object containing the data to be retrieved
            pk: The primary key of the district

        Returns:
            Response: The response object containing the retrieved district data
        """
        try:
            district = District.objects.get(id=pk, is_active=True)
        except District.DoesNotExist:
            return Response({'message': 'District not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullDistrictSerializer(district)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        """
        List all districts

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of districts
        """
        query = request.query_params.get('query', None)
        queryset = District.objects.filter(is_active=True).order_by('name')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = FullDistrictSerializer(page_obj, many=True)
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
            results = FullDistrictSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)



# TODO: ADD VIEW YOUR OWN DISTRICT
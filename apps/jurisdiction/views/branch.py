# views.py
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.jurisdiction.models import Branch
from apps.jurisdiction.serializers.branch import BranchSerializer, FullBranchSerializer
from apps.shared.literals import ADD_BRANCH, UPDATE_BRANCH, DELETE_BRANCH, VIEW_BRANCHES
from apps.shared.utils.permissions import UserPermission


class BranchViewSet(viewsets.GenericViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()

    def get_permissions(self):
        permissions = {
            'create': ADD_BRANCH,
            'update': UPDATE_BRANCH,
            'destroy': DELETE_BRANCH,
            'list': VIEW_BRANCHES,
            'retrieve': VIEW_BRANCHES
        }
        if self.action in ['list']:
            return [IsAuthenticated()]
        user_permission = permissions[self.action]
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        request.data['created_by'] = request.user.id
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            branch = serializer.save()
            return Response(FullBranchSerializer(branch).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            branch = Branch.objects.get(id=pk, is_active=True)
        except Branch.DoesNotExist:
            return Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            updated_branch = serializer.save()
            branch.date_modified = datetime.now()
            branch.modified_by = request.user
            branch.save()
            return Response(FullBranchSerializer(updated_branch).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            branch = self.get_queryset().get(id=pk, is_active=True)
            branch.soft_delete(owner=request.user)
            return Response({'message': 'Branch deleted successfully'}, status=status.HTTP_200_OK)
        except Branch.DoesNotExist:
            return Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        try:
            branch = Branch.objects.get(id=pk, is_active=True)
        except Branch.DoesNotExist:
            return Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullBranchSerializer(branch)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        query = request.query_params.get('query', None)
        queryset = Branch.objects.filter(is_active=True).order_by('name')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = FullBranchSerializer(page_obj, many=True)
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
            results = FullBranchSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)


# TODO: ADD VIEW YOUR OWN BRANCH

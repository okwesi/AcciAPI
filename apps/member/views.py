from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.member.models import Member
from apps.member.serializer import MemberSerializer, ShortMemberSerializer, FullMemberSerializer, BulkMemberSerializer
from apps.shared.literals import (
    ADD_MEMBER, UPDATE_MEMBER, DELETE_MEMBER, VIEW_MEMBERS, LIST_BRANCH_MEMBERS,
    LIST_DISTRICT_MEMBERS, LIST_AREA_MEMBERS
)
from apps.shared.utils.permissions import UserPermission

User = get_user_model()


class MemberViewSet(viewsets.GenericViewSet):
    serializer_class = MemberSerializer
    queryset = Member.objects.filter(is_active=True)

    def get_permissions(self):
        permissions = {
            'create': ADD_MEMBER,
            'update': UPDATE_MEMBER,
            'destroy': DELETE_MEMBER,
            'list': VIEW_MEMBERS,
            'retrieve': VIEW_MEMBERS,
            'list_branch_members': LIST_BRANCH_MEMBERS,
            'list_district_members': LIST_DISTRICT_MEMBERS,
            'list_area_members': LIST_AREA_MEMBERS,
            'get_short_members': VIEW_MEMBERS,
            'bulk_import_members': VIEW_MEMBERS
        }
        user_permission = permissions[self.action]
        print(f'user: {self.request.user}'
              f' permission to check:{user_permission}')
        return [
            IsAuthenticated(), UserPermission(user_permission)
        ]

    def create(self, request):
        """
        Create a new member

        Args:
            request: The request object containing the data to be created

        Returns:
            Response: The response object containing the created member data
        """
        serializer = MemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            member = serializer.save()
            try:
                user = User.objects.get(phone_number=member.phone_number)
                user.member = member
            except User.DoesNotExist:
                pass
            return Response(MemberSerializer(member).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update a member

        Args:
            request: The request object containing the data to be updated
            pk: The primary key of the member

        Returns:
            Response: The response object containing the updated member data
        """
        try:
            member = Member.objects.get(id=pk, is_active=True)
        except Member.DoesNotExist:
            return Response({'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            updated_member = serializer.save()
            member.date_modified = datetime.now()
            member.modified_by = request.user
            member.save()
            return Response(MemberSerializer(updated_member).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a member

        Args:
            request: The request object containing the data to be deleted
            pk: The primary key of the member

        Returns:
            Response: The response object containing the deleted member data
        """
        try:
            member = self.get_queryset().get(id=pk, is_active=True)
            fields_to_encrypt = ['email', 'phone_number']
            member.soft_delete(owner=request.user, fields_to_encrypt=fields_to_encrypt)
            return Response({'message': 'Member deleted successfully'}, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """
        Retrieve a member

        Args:
            request: The request object containing the query string
            pk: The primary key of the member

        Returns:
            Response: The response object containing the retrieved member data
        """
        try:
            member = Member.objects.get(id=pk, is_active=True)
        except Member.DoesNotExist:
            return Response({'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        """
        List all members

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of members
        """
        query = request.query_params.get('query', None)
        queryset = self.get_queryset().filter(is_active=True).order_by('first_name')

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = ShortMemberSerializer(page_obj, many=True)
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
            results = ShortMemberSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='list-branch-members')
    def list_branch_members(self, request):
        """
        List all members from the users branch

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of members
       """
        query = request.query_params.get('query', None)
        print(request.user.branch)
        queryset = Member.objects.filter(branch=request.user.branch, is_active=True).order_by('first_name')

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = ShortMemberSerializer(page_obj, many=True)
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
            results = ShortMemberSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='list-district-members')
    def list_district_members(self, request):
        """
        List all members from the users district

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of members
       """
        query = request.query_params.get('query', None)
        queryset = Member.objects.filter(
                    branch__district=request.user.branch.district, is_active=True).order_by('first_name')

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = ShortMemberSerializer(page_obj, many=True)
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
            results = ShortMemberSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='list-area-members')
    def list_area_members(self, request):
        """
        List all members from the users district

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of members
       """
        query = request.query_params.get('query', None)
        queryset = Member.objects.filter(
            branch__district__area=request.user.branch.district.area, is_active=True).order_by('first_name')

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query)
            )

        page_number = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)
        if page_size and page_number:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = ShortMemberSerializer(page_obj, many=True)
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
            results = ShortMemberSerializer(queryset, many=True).data

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get-short-members')
    def get_short_members(self, request):
        """
        List all members

        Args:
            request: The request object containing the query string

        Returns:
            Response: The response object containing the list of members
       """
        query = request.query_params.get('query', None)
        queryset = Member.objects.filter(is_active=True).order_by('first_name')

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(phone_number__iexact=query) |
                Q(email__iexact=query)
            )
        return Response(ShortMemberSerializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_import_members(self, request):
        """
        Bulk import members with error handling for duplicates

        Args:
            request: The request object containing the list of members to import

        Returns:
            Response: The response object containing successfully created members
            and a list of members that could not be saved
        """
        members_data = request.data
        successful_members = []
        failed_members = []
        for member_data in members_data:
            try:
                existing_member = Member.objects.filter(
                    Q(phone_number=member_data.get('phone_number')) |
                    Q(email=member_data.get('email'))
                ).first()

                if existing_member:
                    # If member exists, add to failed members
                    member_data['error'] = 'Duplicate phone number or email'
                    failed_members.append(member_data)
                    continue

                # Validate and create member
                serializer = BulkMemberSerializer(data=member_data, context={'request': request})
                if serializer.is_valid():
                    member = serializer.save(branch=request.user.branch, created_by=request.user)
                    successful_members.append(serializer.data)
                else:
                    member_data['errors'] = serializer.errors
                    failed_members.append(member_data)

            except Exception as e:
                # member_data['error'] = e
                failed_members.append(member_data)

        return Response({
            'failed_members': failed_members,
            'total_processed': len(members_data),
            'total_successful': len(successful_members),
            'total_failed': len(failed_members)
        }, status=status.HTTP_201_CREATED)

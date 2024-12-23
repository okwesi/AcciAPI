import decimal

from django.core.paginator import Paginator
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.donation.models import Donation
from apps.donation.serializers.donation import DonationSerializer, ListDonationSerializer, MakeDonationSerializer
from apps.shared.general import GENERAL_SUCCESS_RESPONSE
from apps.shared.literals import CREATE_DONATION, DELETE_DONATION, UPDATE_DONATION
from apps.shared.utils.permissions import UserPermission


class DonationViewSet(viewsets.GenericViewSet):
    queryset = Donation.objects.all()

    def get_permissions(self):
        permissions = {
            'create': CREATE_DONATION,
            'update': UPDATE_DONATION,
            'destroy': DELETE_DONATION,
        }
        user_permission = permissions.get(self.action)
        if user_permission:
            return [IsAuthenticated(), UserPermission(user_permission)]
        return [IsAuthenticated()]

    def create(self, request):
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            donation = Donation.objects.get(pk=pk, is_active=True)
            serializer = DonationSerializer(donation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Donation.DoesNotExist:
            return Response({"message": "Donation not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            donation = Donation.objects.get(pk=pk, is_active=True)
            donation.soft_delete(owner=request.user)
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except Donation.DoesNotExist:
            return Response({"message": "Donation not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        donations = Donation.objects.filter(is_active=True).order_by('-date_created')
        paginator = Paginator(donations, page_size)
        page_obj = paginator.get_page(page)

        serializer = ListDonationSerializer(instance=page_obj.object_list, many=True, context={'request': request})
        results = serializer.data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': donations.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='make-donation')
    def make_donation(self, request):
        print(request.data)
        serializer = MakeDonationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            donation = serializer.save()
            return Response(MakeDonationSerializer(donation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


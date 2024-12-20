from django.core.paginator import Paginator
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.donation.models import Pledge
from apps.donation.serializers.pledge import ListPledgeSerializer, PledgeSerializer, RedeemPledgeSerializer


class PledgeViewSet(viewsets.GenericViewSet):
    queryset = Pledge.objects.all()

    def get_permissions(self):
        return [IsAuthenticated()]

    def create(self, request):
        serializer = PledgeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        pledges = Pledge.objects.filter(is_active=True, user=request.user).order_by('-redeem_date')
        paginator = Paginator(pledges, page_size)
        page_obj = paginator.get_page(page)

        results = ListPledgeSerializer(instance=page_obj.object_list, many=True).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': pledges.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='redeem-pledge')
    def redeem_pledge(self, request):
        serializer = RedeemPledgeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            redeemed_data = serializer.save()
            return Response(redeemed_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

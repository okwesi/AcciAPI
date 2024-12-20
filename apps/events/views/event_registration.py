from django.core.paginator import Paginator
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.events.models import EventRegistration
from apps.events.serializers.event_registration import EventRegistrationSerializer, RegisteredEventSerializer


class EventRegistrationViewSet(viewsets.GenericViewSet):
    queryset = EventRegistration.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        serializer = EventRegistrationSerializer(data=request.data,
                                                 context={'request': request})
        if serializer.is_valid():
            registration = serializer.save()
            return Response(
                EventRegistrationSerializer(registration).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        user = request.user
        registrations = EventRegistration.objects.filter(user=user).select_related('event').order_by("-id")
        paginator = Paginator(registrations, page_size)
        page_obj = paginator.get_page(page)

        results = RegisteredEventSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': registrations.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

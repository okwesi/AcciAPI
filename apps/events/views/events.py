from django.core.paginator import Paginator
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.events.models import Event
from apps.events.serializers.events import EventSerializer, ListEventsSerializer
from apps.shared.general import GENERAL_SUCCESS_RESPONSE
from apps.shared.literals import CREATE_EVENT, DELETE_EVENT, UPDATE_EVENT
from apps.shared.utils.permissions import UserPermission


class EventViewSet(viewsets.GenericViewSet):
    queryset = Event.objects.all()

    def get_permissions(self):
        permissions = {
            'create': CREATE_EVENT,
            'update': UPDATE_EVENT,
            'destroy': DELETE_EVENT,
        }
        user_permission = permissions.get(self.action, None)
        if user_permission:
            return [IsAuthenticated(), UserPermission(user_permission)]
        return [IsAuthenticated()]

    def create(self, request):
        serializer = EventSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk, is_active=True)
            event.delete()
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        events = Event.objects.filter(is_active=True).order_by('-start_datetime')
        paginator = Paginator(events, page_size)
        page_obj = paginator.get_page(page)

        results = ListEventsSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': events.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

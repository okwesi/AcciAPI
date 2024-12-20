from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.events.views.event_registration import EventRegistrationViewSet
from apps.events.views.events import EventViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'events/event', EventViewSet, basename='event')
router.register(r'events/registration', EventRegistrationViewSet, basename='registration')


urlpatterns = [
    path('', include(router.urls)),
]

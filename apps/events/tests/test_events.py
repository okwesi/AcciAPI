import json

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factory import UserFactory
from apps.events.models import Event, EventAmount
from apps.events.tests.factories import EventAmountFactory, EventFactory
from apps.shared.literals import CREATE_EVENT, DELETE_EVENT, UPDATE_EVENT


# pytest -v apps/events/tests/test_events.py

@pytest.mark.django_db
class TestEventViewSet:
    def setup_method(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def _assign_permission(self, codename):
        """Helper method to assign permission to user."""
        permission = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(permission)
        self.user.save()

    def test_create_event_without_permission(self):
        url = reverse('event-list')
        payload = {'title': 'Event without permission'}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_event_with_valid_data(self):
        self._assign_permission(CREATE_EVENT)
        url = reverse('event-list')
        payload = {
            'title': 'New Event',
            'location': 'Conference Hall',
            'start_datetime': '2024-11-15T09:00:00Z',
            'end_datetime': '2024-11-15T17:00:00Z',
            'description': 'An exciting new event.',
            'event_amounts': [{'amount': 100, 'currency': 'USD'}],
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        event = Event.objects.get(title='New Event')
        assert event.location == 'Conference Hall'
        assert event.event_amounts.count() == 1
        assert event.event_amounts.first().currency == 'USD'

    def test_create_event_missing_required_fields(self):
        self._assign_permission(CREATE_EVENT)
        url = reverse('event-list')
        payload = {'title': '', 'location': 'Unknown'}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data

    # UPDATE Event Tests
    def test_update_event_without_permission(self):
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        payload = {'title': 'Unauthorized Update'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_event(self):
        self._assign_permission(UPDATE_EVENT)
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        payload = {'title': 'Partially Updated Event'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.title == 'Partially Updated Event'

    def test_update_event_replace_event_amounts(self):
        self._assign_permission(UPDATE_EVENT)
        event = EventFactory()
        EventAmountFactory(event=event, amount=150)
        url = reverse('event-detail', args=[event.id])
        payload = {
            'event_amounts': [{'amount': 200, 'currency': 'EUR'}]
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.event_amounts.count() == 1
        assert event.event_amounts.first().amount == 200

    def test_delete_event_without_permission(self):
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_event_with_permission(self):
        self._assign_permission(DELETE_EVENT)
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert not Event.objects.filter(id=event.id).exists()

    def test_delete_nonexistent_event(self):
        self._assign_permission(DELETE_EVENT)
        url = reverse('event-detail', args=[99999])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # LIST Event Tests
    def test_list_events_with_permission(self):
        EventFactory.create_batch(3)
        url = reverse('event-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_list_events_with_pagination(self):
        EventFactory.create_batch(10)
        url = reverse('event-list') + '?page=2&page_size=3'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        assert response.data['pagination']['page'] == 2

    def test_create_event_with_missing_event_amounts(self):
        self._assign_permission(CREATE_EVENT)
        url = reverse('event-list')
        payload = {
            'title': 'Event without Amounts',
            'location': 'Main Hall',
            'start_datetime': '2024-11-15T09:00:00Z',
            'end_datetime': '2024-11-15T17:00:00Z',
            'description': 'Event missing amounts field.',
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'event_amounts' in response.data

    def test_create_event_with_invalid_datetime_format(self):
        self._assign_permission(CREATE_EVENT)
        url = reverse('event-list')
        payload = {
            'title': 'Invalid DateTime Format Event',
            'location': 'Invalid Hall',
            'start_datetime': 'InvalidDate',
            'end_datetime': 'InvalidDate',
            'description': 'This should fail due to datetime format.',
            'event_amounts': [{'amount': 100, 'currency': 'USD'}],
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'start_datetime' in response.data
        assert 'end_datetime' in response.data

    def test_create_event_with_negative_amount(self):
        self._assign_permission(CREATE_EVENT)
        url = reverse('event-list')
        payload = {
            'title': 'Negative Amount Event',
            'location': 'Conference Center',
            'start_datetime': '2024-11-15T09:00:00Z',
            'end_datetime': '2024-11-15T17:00:00Z',
            'description': 'An event with a negative amount.',
            'event_amounts': [{'amount': -100, 'currency': 'USD'}],
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'event_amounts' in response.data

    def test_update_event_with_empty_payload(self):
        self._assign_permission(UPDATE_EVENT)
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        response = self.client.put(url, data=json.dumps({}), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_event_start_date_after_end_date(self):
        self._assign_permission(UPDATE_EVENT)
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        payload = {
            'start_datetime': '2024-11-16T09:00:00Z',
            'end_datetime': '2024-11-15T17:00:00Z',
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'start_datetime' in response.data or 'end_datetime' in response.data

    def test_partial_update_event_with_nonexistent_field(self):
        self._assign_permission(UPDATE_EVENT)
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        payload = {'nonexistent_field': 'This should not work'}
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_event_without_permissions(self):
        event = EventFactory()
        url = reverse('event-detail', args=[event.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_event_with_associated_amounts(self):
        self._assign_permission(DELETE_EVENT)
        event = EventFactory()
        EventAmountFactory.create_batch(3, event=event)
        url = reverse('event-detail', args=[event.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert not Event.objects.filter(id=event.id).exists()
        assert not EventAmount.objects.filter(event=event).exists()

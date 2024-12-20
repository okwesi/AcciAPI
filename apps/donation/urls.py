from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.donation.views.donation import DonationViewSet
from apps.donation.views.pledge import PledgeViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'donation', DonationViewSet, basename='donation')
router.register(r'pledge', PledgeViewSet, basename='pledge')


urlpatterns = [
    path('', include(router.urls)),
]

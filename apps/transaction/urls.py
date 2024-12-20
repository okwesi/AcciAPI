from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentTransactionViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'transactions', PaymentTransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
    path('complete-payment', PaymentTransactionViewSet.as_view({'get': 'complete_payment'}))
]

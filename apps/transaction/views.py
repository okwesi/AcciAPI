from datetime import datetime

from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.donation.models import Donation
from apps.events.models import Event, EventRegistration
from apps.shared.literals import COMPLETE_PAYMENT_TEMPLATE
from apps.transaction.models import PaymentTransaction
from apps.transaction.serializers import PaymentTransactionSerializer, PaymentVerificationSerializer


class PaymentTransactionViewSet(viewsets.GenericViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    def get_permissions(self):
        if self.action == 'complete_payment':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='list-verified-transactions')
    def list_verified_transactions(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        category = request.query_params.get('category', None)

        transactions = PaymentTransaction.objects.filter(category=category, is_verified=True,
                                                         user=request.user).order_by(
            '-payment_completed_at')
        paginator = Paginator(transactions, page_size)
        page_obj = paginator.get_page(page)

        results = PaymentTransactionSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': transactions.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='complete-payment')
    @transaction.atomic
    def complete_payment(self, request):
        """Checks payment status with Paystack and updates the transaction."""
        reference = request.GET.get("reference")
        if not reference:
            return Response({"error": "Reference is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            PaymentTransaction.objects.get(reference=reference)
            serializer = PaymentVerificationSerializer(data={"reference": reference})
            if serializer.is_valid():
                payment = serializer.process_verification()
                category_model_mapping = {
                    'event': EventRegistration,
                    'donation': Donation,
                }
                model = category_model_mapping.get(payment.category)
                payment_category_title = None
                if model:
                    payment_category = get_object_or_404(model, id=payment.category_object_id)
                    payment_category_title = (
                        payment_category.event.title if payment.category == 'event' else payment_category.title
                    )
                html_content = render_to_string(
                    COMPLETE_PAYMENT_TEMPLATE,
                    {
                        'payment': payment,
                        'payment_category_title': payment_category_title,
                        'payment_completed_at': datetime.fromisoformat(
                            payment.payment_completed_at.replace("Z", "")).strftime("%d %b %Y, %I:%M %p")
                    }
                )
                return HttpResponse(html_content, content_type='text/html')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PaymentTransaction.DoesNotExist:
            return Response({"message": "Payment Transaction is verified already"}, status=status.HTTP_404_NOT_FOUND)

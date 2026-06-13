import uuid
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, Transaction
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer,
    ProcessPaymentSerializer, RefundSerializer,
)
from .services import notify_order_payment_success, notify_order_payment_failed


def is_staff_or_admin(user):
    return getattr(user, 'role', None) in ('admin', 'staff')


class PaymentListView(APIView):
    """GET /api/payments/ - list payments for current user (or all for staff)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_staff_or_admin(request.user):
            payments = Payment.objects.prefetch_related('transactions').all()
            uid = request.query_params.get('user_id')
            if uid:
                payments = payments.filter(user_id=uid)
        else:
            payments = Payment.objects.prefetch_related('transactions').filter(user_id=request.user.id)

        status_f = request.query_params.get('status')
        if status_f:
            payments = payments.filter(status=status_f)

        return Response({'count': payments.count(), 'results': PaymentSerializer(payments, many=True).data})


class PaymentDetailView(APIView):
    """GET /api/payments/<id>/"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            if is_staff_or_admin(user):
                return Payment.objects.prefetch_related('transactions').get(pk=pk)
            return Payment.objects.prefetch_related('transactions').get(pk=pk, user_id=user.id)
        except Payment.DoesNotExist:
            return None

    def get(self, request, pk):
        payment = self.get_object(pk, request.user)
        if not payment:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


class ProcessPaymentView(APIView):
    """POST /api/payments/<id>/process/ - simulate payment processing"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk, user_id=request.user.id)
        except Payment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status != 'pending':
            return Response({'detail': f'Payment already {payment.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mock payment processing
        if payment.payment_method == 'cod':
            # COD: always succeeds immediately (payment on delivery)
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.gateway_response = {'provider': 'COD', 'message': 'Payment on delivery confirmed.'}
        elif payment.payment_method == 'bank':
            bank_ref = request.data.get('bank_ref', '')
            if not bank_ref:
                return Response({'detail': 'bank_ref is required for bank transfer.'}, status=status.HTTP_400_BAD_REQUEST)
            # Mock: bank transfer succeeds
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.gateway_response = {'provider': 'MOCK_BANK', 'bank_ref': bank_ref}
        elif payment.payment_method == 'ewallet':
            # Mock: ewallet succeeds
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.gateway_response = {'provider': 'MOCK_EWALLET', 'transaction_id': str(uuid.uuid4())}

        payment.save()

        # Create transaction record
        Transaction.objects.create(
            payment=payment,
            type='charge',
            amount=payment.amount,
            note=f'{payment.payment_method} payment processed.',
        )

        # Notify order-service
        if payment.status == 'success':
            notify_order_payment_success(payment.order_id)
        else:
            notify_order_payment_failed(payment.order_id)

        return Response(PaymentSerializer(payment).data)


class RefundPaymentView(APIView):
    """POST /api/payments/<id>/refund/ - admin/staff only"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RefundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status != 'success':
            return Response({'detail': 'Only successful payments can be refunded.'}, status=status.HTTP_400_BAD_REQUEST)

        refund_amount = serializer.validated_data.get('amount', payment.amount)
        reason        = serializer.validated_data.get('reason', 'Admin refund')

        payment.status = 'refunded'
        payment.save(update_fields=['status', 'updated_at'])

        Transaction.objects.create(
            payment=payment,
            type='refund',
            amount=refund_amount,
            note=reason,
        )
        return Response(PaymentSerializer(payment).data)


class PaymentInternalCreateView(APIView):
    """Internal: POST /api/payments/internal/create/ - called by order-service."""
    permission_classes = []

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Avoid duplicate
        payment, created = Payment.objects.get_or_create(
            order_id=data['order_id'],
            defaults={
                'user_id':        data.get('user_id', 0),
                'amount':         data['amount'],
                'payment_method': data['payment_method'],
                'status':         'pending',
            },
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

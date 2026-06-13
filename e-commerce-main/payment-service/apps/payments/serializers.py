from rest_framework import serializers
from .models import Payment, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Transaction
        fields = ['id', 'type', 'amount', 'reference', 'note', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model  = Payment
        fields = [
            'id', 'order_id', 'user_id', 'amount', 'payment_method',
            'status', 'transaction_ref', 'gateway_response', 'paid_at',
            'transactions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'transaction_ref', 'created_at', 'updated_at']


class CreatePaymentSerializer(serializers.Serializer):
    """Used by order-service internally."""
    order_id       = serializers.IntegerField()
    amount         = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=['cod', 'bank', 'ewallet'])
    user_id        = serializers.IntegerField(required=False, default=0)


class ProcessPaymentSerializer(serializers.Serializer):
    """Customer triggers payment processing."""
    payment_id     = serializers.IntegerField()
    # For bank/ewallet: optional transaction details
    bank_ref       = serializers.CharField(required=False, allow_blank=True)
    ewallet_token  = serializers.CharField(required=False, allow_blank=True)


class RefundSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

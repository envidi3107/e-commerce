from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_sku',
                  'product_thumbnail', 'unit_price', 'quantity', 'subtotal']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderStatusHistory
        fields = ['id', 'status', 'note', 'changed_by', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items   = OrderItemSerializer(many=True, read_only=True)
    history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'user_id', 'status', 'payment_method', 'payment_status',
            'shipping_address', 'subtotal', 'shipping_fee', 'discount', 'total',
            'notes', 'payment_id', 'shipment_id',
            'items', 'history',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_id', 'subtotal', 'total', 'payment_id',
                            'shipment_id', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Payload to create an order from cart."""
    payment_method   = serializers.ChoiceField(choices=['cod', 'bank', 'ewallet'])
    shipping_address = serializers.DictField()
    notes            = serializers.CharField(required=False, allow_blank=True)
    shipping_fee     = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount         = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
    )
    note   = serializers.CharField(required=False, allow_blank=True)

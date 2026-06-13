from rest_framework import serializers
from .models import Shipment, TrackingEvent


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TrackingEvent
        fields = ['id', 'status', 'location', 'description', 'timestamp']


class ShipmentSerializer(serializers.ModelSerializer):
    events = TrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model  = Shipment
        fields = [
            'id', 'order_id', 'tracking_number', 'provider', 'status',
            'shipping_address', 'estimated_delivery', 'actual_delivery',
            'shipping_fee', 'notes', 'events',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'tracking_number', 'created_at', 'updated_at']


class CreateShipmentSerializer(serializers.Serializer):
    """Used internally by order-service."""
    order_id         = serializers.IntegerField()
    shipping_address = serializers.DictField()
    shipping_fee     = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    provider         = serializers.ChoiceField(choices=['ghn', 'ghtk', 'vnpost', 'mock'], default='mock')


class UpdateShipmentStatusSerializer(serializers.Serializer):
    status      = serializers.ChoiceField(choices=[
        'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed', 'returned',
    ])
    location    = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

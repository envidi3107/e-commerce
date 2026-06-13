from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model  = CartItem
        fields = [
            'id', 'product_id', 'product_name', 'product_price',
            'product_thumbnail', 'quantity', 'subtotal', 'added_at', 'updated_at',
        ]
        read_only_fields = ['id', 'product_name', 'product_price', 'product_thumbnail', 'added_at', 'updated_at']


class CartItemAddSerializer(serializers.Serializer):
    """Used when adding an item - validates input, then fetches product info."""
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    items       = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model  = Cart
        fields = ['id', 'user_id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']

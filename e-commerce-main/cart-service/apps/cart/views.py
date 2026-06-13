import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemAddSerializer, CartItemUpdateSerializer
)
from .services import fetch_product


def get_or_create_cart(user_id):
    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    return cart


class CartView(APIView):
    """GET  /api/cart/  - retrieve current user's cart
       DELETE /api/cart/ - clear cart"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user.id)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart = get_or_create_cart(request.user.id)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared.'})


class CartItemListView(APIView):
    """POST /api/cart/items/ - add item to cart"""
    permission_classes = [IsAuthenticated]

    logger = logging.getLogger(__name__)

    def post(self, request):
        # Debug logging for incoming auth header and remote address
        self.logger.warning(
            "CartItemListView.post request: REMOTE_ADDR=%s AUTH=%s data=%s",
            request.META.get('REMOTE_ADDR'),
            request.META.get('HTTP_AUTHORIZATION'),
            request.data,
        )

        serializer = CartItemAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        # Fetch product info from product-service
        token = request.auth if isinstance(request.auth, str) else str(request.auth)
        product = fetch_product(product_id, token=token)
        if not product:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        if product.get('status') != 'active':
            return Response({'detail': 'Product is not available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check inventory
        inventory = product.get('inventory', {})
        available = inventory.get('available', 0)
        if available < quantity:
            return Response({'detail': f'Only {available} item(s) available.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request.user.id)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={
                'product_name': product['name'],
                'product_price': product['price'],
                'product_thumbnail': product.get('thumbnail', ''),
                'quantity': quantity,
            },
        )
        if not created:
            new_qty = item.quantity + quantity
            if new_qty > available:
                return Response({'detail': f'Only {available} item(s) available.'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = new_qty
            item.product_price = product['price']  # refresh price
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """PUT  /api/cart/items/<id>/ - update quantity
       DELETE /api/cart/items/<id>/ - remove item"""
    permission_classes = [IsAuthenticated]

    def get_item(self, request, item_id):
        try:
            return CartItem.objects.get(id=item_id, cart__user_id=request.user.id)
        except CartItem.DoesNotExist:
            return None

    def put(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = serializer.validated_data['quantity']
        item.save()
        cart = get_or_create_cart(request.user.id)
        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        cart = get_or_create_cart(request.user.id)
        return Response(CartSerializer(cart).data)


class CartInternalView(APIView):
    """Internal: GET /api/cart/internal/<user_id>/ - used by order-service."""
    permission_classes = []  # internal call only (secured by network policy)

    def get(self, request, user_id):
        cart = get_or_create_cart(user_id)
        return Response(CartSerializer(cart).data)

    def delete(self, request, user_id):
        """Clear cart after order is placed."""
        cart = get_or_create_cart(user_id)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared after order.'})

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
from .services import get_cart, clear_cart, notify_payment_service, notify_shipping_service


def is_staff_or_admin(user):
    return getattr(user, 'role', None) in ('admin', 'staff')


class OrderListView(APIView):
    """GET  /api/orders/ - list orders
       POST /api/orders/ - create order from cart"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_staff_or_admin(request.user):
            orders = Order.objects.prefetch_related('items', 'history').all()
            # Filter by user_id if provided
            uid = request.query_params.get('user_id')
            if uid:
                orders = orders.filter(user_id=uid)
        else:
            orders = Order.objects.prefetch_related('items', 'history').filter(user_id=request.user.id)

        status_f = request.query_params.get('status')
        if status_f:
            orders = orders.filter(status=status_f)

        return Response({
            'count':   orders.count(),
            'results': OrderSerializer(orders, many=True).data,
        })

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Fetch cart
        cart = get_cart(request.user.id)
        if not cart or not cart.get('items'):
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build order
        subtotal = Decimal(str(cart['total_price']))
        shipping_fee = Decimal(str(data.get('shipping_fee', 0)))
        discount     = Decimal(str(data.get('discount', 0)))
        total = subtotal + shipping_fee - discount

        order = Order.objects.create(
            user_id=request.user.id,
            status='pending',
            payment_method=data['payment_method'],
            shipping_address=data['shipping_address'],
            notes=data.get('notes', ''),
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            discount=discount,
            total=total,
        )

        # Create order items from cart
        for ci in cart['items']:
            OrderItem.objects.create(
                order=order,
                product_id=ci['product_id'],
                product_name=ci['product_name'],
                product_thumbnail=ci.get('product_thumbnail', ''),
                unit_price=Decimal(str(ci['product_price'])),
                quantity=ci['quantity'],
            )

        # Record history
        OrderStatusHistory.objects.create(order=order, status='pending', note='Order created.')

        # Clear cart
        clear_cart(request.user.id)

        # Notify payment service
        payment_data = notify_payment_service(order.id, total, data['payment_method'])
        if payment_data:
            order.payment_id = payment_data.get('id')
            order.save(update_fields=['payment_id'])

        # Notify shipping service
        shipping_data = notify_shipping_service(order.id, data['shipping_address'])
        if shipping_data:
            order.shipment_id = shipping_data.get('id')
            order.save(update_fields=['shipment_id'])

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """GET  /api/orders/<id>/
       DELETE /api/orders/<id>/ - cancel order"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            if is_staff_or_admin(user):
                return Order.objects.prefetch_related('items', 'history').get(pk=pk)
            return Order.objects.prefetch_related('items', 'history').get(pk=pk, user_id=user.id)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)

    def delete(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.status not in ('pending', 'confirmed'):
            return Response({'detail': 'Cannot cancel order at this stage.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status='cancelled',
            note='Cancelled by user.', changed_by=request.user.id,
        )
        return Response(OrderSerializer(order).data)


class OrderStatusUpdateView(APIView):
    """PUT /api/orders/<id>/status/ - staff/admin only"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateOrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']
        note       = serializer.validated_data.get('note', '')
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status=new_status,
            note=note, changed_by=request.user.id,
        )
        return Response(OrderSerializer(order).data)


class OrderInternalUpdateView(APIView):
    """Internal: PATCH /api/orders/internal/<id>/ - used by payment/shipping service."""
    permission_classes = []

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        payment_status = request.data.get('payment_status')
        order_status   = request.data.get('status')

        if payment_status:
            order.payment_status = payment_status
        if order_status:
            order.status = order_status
            OrderStatusHistory.objects.create(order=order, status=order_status, note='Updated by internal service.')
        order.save()
        return Response({'message': 'Order updated.'})

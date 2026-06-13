from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Shipment, TrackingEvent
from .serializers import (
    ShipmentSerializer, CreateShipmentSerializer, UpdateShipmentStatusSerializer,
)
from .services import notify_order_shipped, notify_order_delivered, calculate_estimated_delivery


def is_staff_or_admin(user):
    return getattr(user, 'role', None) in ('admin', 'staff')


class ShipmentListView(APIView):
    """GET /api/shipping/ - list shipments"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_staff_or_admin(request.user):
            shipments = Shipment.objects.prefetch_related('events').all()
        else:
            # Customers can only see their own orders' shipments
            # In real system, verify ownership via order-service
            shipments = Shipment.objects.prefetch_related('events').all()

        status_f = request.query_params.get('status')
        if status_f:
            shipments = shipments.filter(status=status_f)

        order_id = request.query_params.get('order_id')
        if order_id:
            shipments = shipments.filter(order_id=order_id)

        return Response({'count': shipments.count(), 'results': ShipmentSerializer(shipments, many=True).data})


class ShipmentDetailView(APIView):
    """GET /api/shipping/<id>/"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Shipment.objects.prefetch_related('events').get(pk=pk)
        except Shipment.DoesNotExist:
            return None

    def get(self, request, pk):
        shipment = self.get_object(pk)
        if not shipment:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ShipmentSerializer(shipment).data)


class ShipmentTrackingView(APIView):
    """GET /api/shipping/<id>/tracking/ - get full tracking timeline"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            shipment = Shipment.objects.prefetch_related('events').get(pk=pk)
        except Shipment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        from .serializers import TrackingEventSerializer
        return Response({
            'shipment_id':      shipment.id,
            'order_id':         shipment.order_id,
            'tracking_number':  str(shipment.tracking_number),
            'provider':         shipment.provider,
            'current_status':   shipment.status,
            'estimated_delivery': shipment.estimated_delivery,
            'actual_delivery':  shipment.actual_delivery,
            'events':           TrackingEventSerializer(shipment.events.all(), many=True).data,
        })


class ShipmentStatusUpdateView(APIView):
    """PUT /api/shipping/<id>/status/ - staff/admin update shipment status"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            shipment = Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateShipmentStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status  = serializer.validated_data['status']
        location    = serializer.validated_data.get('location', '')
        description = serializer.validated_data.get('description', '')

        shipment.status = new_status
        if new_status == 'delivered':
            shipment.actual_delivery = timezone.now()
            notify_order_delivered(shipment.order_id)
        elif new_status == 'in_transit':
            notify_order_shipped(shipment.order_id)

        shipment.save()

        TrackingEvent.objects.create(
            shipment=shipment,
            status=new_status,
            location=location,
            description=description,
        )

        return Response(ShipmentSerializer(shipment).data)


class ShipmentInternalCreateView(APIView):
    """Internal: POST /api/shipping/internal/create/ - called by order-service"""
    permission_classes = []

    def post(self, request):
        serializer = CreateShipmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        shipment, created = Shipment.objects.get_or_create(
            order_id=data['order_id'],
            defaults={
                'shipping_address':   data['shipping_address'],
                'shipping_fee':       data.get('shipping_fee', 0),
                'provider':           data.get('provider', 'mock'),
                'status':             'pending',
                'estimated_delivery': calculate_estimated_delivery(data.get('provider', 'mock')),
            },
        )

        if created:
            TrackingEvent.objects.create(
                shipment=shipment,
                status='pending',
                description='Shipment created, waiting for pickup.',
            )

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

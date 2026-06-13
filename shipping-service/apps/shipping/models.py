from django.db import models
import uuid


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('picked_up',  'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',  'Delivered'),
        ('failed',     'Failed'),
        ('returned',   'Returned'),
    ]

    PROVIDER_CHOICES = [
        ('ghn',   'Giao Hàng Nhanh'),
        ('ghtk',  'Giao Hàng Tiết Kiệm'),
        ('vnpost', 'VN Post'),
        ('mock',  'Mock Provider'),
    ]

    order_id         = models.IntegerField(unique=True, db_index=True)
    tracking_number  = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    provider         = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='mock')
    status           = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.JSONField()
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery  = models.DateTimeField(null=True, blank=True)
    shipping_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment#{self.id} order={self.order_id} [{self.status}]"


class TrackingEvent(models.Model):
    shipment   = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='events')
    status     = models.CharField(max_length=30)
    location   = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tracking_events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} @ {self.timestamp}"

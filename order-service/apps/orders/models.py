from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod',      'Cash on Delivery'),
        ('bank',     'Bank Transfer'),
        ('ewallet',  'E-Wallet'),
    ]

    user_id          = models.IntegerField(db_index=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status   = models.CharField(max_length=20, default='unpaid')
    shipping_address = models.JSONField()          # {name, phone, address, city, district, ward}
    subtotal         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    # References to other services
    payment_id       = models.IntegerField(null=True, blank=True)
    shipment_id      = models.IntegerField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order#{self.id} user={self.user_id} status={self.status}"


class OrderItem(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id    = models.IntegerField()
    product_name  = models.CharField(max_length=255)
    product_sku   = models.CharField(max_length=100, blank=True)
    product_thumbnail = models.URLField(blank=True)
    unit_price    = models.DecimalField(max_digits=12, decimal_places=2)
    quantity      = models.PositiveIntegerField()
    subtotal      = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class OrderStatusHistory(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status     = models.CharField(max_length=20)
    note       = models.TextField(blank=True)
    changed_by = models.IntegerField(null=True, blank=True)  # user_id
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_history'
        ordering = ['created_at']

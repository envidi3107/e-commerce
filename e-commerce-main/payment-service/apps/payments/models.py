from django.db import models
import uuid


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('success',   'Success'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    METHOD_CHOICES = [
        ('cod',     'Cash on Delivery'),
        ('bank',    'Bank Transfer'),
        ('ewallet', 'E-Wallet'),
    ]

    order_id       = models.IntegerField(unique=True, db_index=True)
    user_id        = models.IntegerField(db_index=True, default=0)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_ref = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at        = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment#{self.id} order={self.order_id} status={self.status}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('charge',  'Charge'),
        ('refund',  'Refund'),
    ]

    payment    = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    reference  = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

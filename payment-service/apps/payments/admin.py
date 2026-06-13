from django.contrib import admin
from .models import Payment, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'order_id', 'amount', 'payment_method', 'status', 'paid_at', 'created_at')
    list_filter   = ('status', 'payment_method')
    inlines       = [TransactionInline]

from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user_id', 'status', 'payment_method', 'total', 'created_at')
    list_filter   = ('status', 'payment_method', 'payment_status')
    search_fields = ('id', 'user_id')
    inlines       = [OrderItemInline, OrderStatusHistoryInline]

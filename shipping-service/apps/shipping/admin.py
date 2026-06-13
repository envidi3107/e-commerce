from django.contrib import admin
from .models import Shipment, TrackingEvent


class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 0
    readonly_fields = ('timestamp',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'order_id', 'tracking_number', 'provider', 'status', 'estimated_delivery')
    list_filter   = ('status', 'provider')
    search_fields = ('tracking_number', 'order_id')
    inlines       = [TrackingEventInline]

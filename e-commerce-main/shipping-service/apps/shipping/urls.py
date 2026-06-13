from django.urls import path
from .views import (
    ShipmentListView, ShipmentDetailView,
    ShipmentTrackingView, ShipmentStatusUpdateView,
    ShipmentInternalCreateView,
)

urlpatterns = [
    path('',                      ShipmentListView.as_view(),         name='shipment-list'),
    path('<int:pk>/',              ShipmentDetailView.as_view(),       name='shipment-detail'),
    path('<int:pk>/tracking/',     ShipmentTrackingView.as_view(),     name='shipment-tracking'),
    path('<int:pk>/status/',       ShipmentStatusUpdateView.as_view(), name='shipment-status'),
    path('internal/create/',       ShipmentInternalCreateView.as_view(), name='shipment-internal-create'),
]

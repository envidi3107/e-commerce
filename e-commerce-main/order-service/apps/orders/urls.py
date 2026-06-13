from django.urls import path
from .views import OrderListView, OrderDetailView, OrderStatusUpdateView, OrderInternalUpdateView

urlpatterns = [
    path('',                      OrderListView.as_view(),         name='order-list'),
    path('<int:pk>/',              OrderDetailView.as_view(),       name='order-detail'),
    path('<int:pk>/status/',       OrderStatusUpdateView.as_view(), name='order-status'),
    path('internal/<int:pk>/',     OrderInternalUpdateView.as_view(), name='order-internal'),
]

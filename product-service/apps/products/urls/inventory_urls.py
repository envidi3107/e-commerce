from django.urls import path
from apps.products.views import InventoryDetailView, InventoryBulkCheckView

urlpatterns = [
    path('<int:product_id>/', InventoryDetailView.as_view(),  name='inventory-detail'),
    path('bulk-check/',       InventoryBulkCheckView.as_view(), name='inventory-bulk-check'),
]

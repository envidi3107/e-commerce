from django.urls import path
from .views import CartView, CartItemListView, CartItemDetailView, CartInternalView

urlpatterns = [
    path('',                          CartView.as_view(),          name='cart'),
    path('items/',                    CartItemListView.as_view(),  name='cart-item-add'),
    path('items/<int:item_id>/',      CartItemDetailView.as_view(), name='cart-item-detail'),
    path('internal/<int:user_id>/',   CartInternalView.as_view(),  name='cart-internal'),
]

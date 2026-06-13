from django.urls import path
from .views import PaymentListView, PaymentDetailView, ProcessPaymentView, RefundPaymentView, PaymentInternalCreateView

urlpatterns = [
    path('',                       PaymentListView.as_view(),          name='payment-list'),
    path('<int:pk>/',               PaymentDetailView.as_view(),        name='payment-detail'),
    path('<int:pk>/process/',       ProcessPaymentView.as_view(),       name='payment-process'),
    path('<int:pk>/refund/',        RefundPaymentView.as_view(),        name='payment-refund'),
    path('internal/create/',        PaymentInternalCreateView.as_view(), name='payment-internal-create'),
]

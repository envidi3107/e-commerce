import requests
from django.conf import settings


def notify_order_payment_success(order_id):
    """Tell order-service that payment succeeded."""
    url = f"{settings.ORDER_SERVICE_URL}/api/orders/internal/{order_id}/"
    try:
        requests.patch(url, json={'payment_status': 'paid', 'status': 'confirmed'}, timeout=5)
    except requests.RequestException:
        pass


def notify_order_payment_failed(order_id):
    url = f"{settings.ORDER_SERVICE_URL}/api/orders/internal/{order_id}/"
    try:
        requests.patch(url, json={'payment_status': 'failed'}, timeout=5)
    except requests.RequestException:
        pass

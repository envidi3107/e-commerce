import requests
from django.conf import settings
from django.utils import timezone


def notify_order_shipped(order_id):
    url = f"{settings.ORDER_SERVICE_URL}/api/orders/internal/{order_id}/"
    try:
        requests.patch(url, json={'status': 'shipped'}, timeout=5)
    except requests.RequestException:
        pass


def notify_order_delivered(order_id):
    url = f"{settings.ORDER_SERVICE_URL}/api/orders/internal/{order_id}/"
    try:
        requests.patch(url, json={'status': 'delivered'}, timeout=5)
    except requests.RequestException:
        pass


def calculate_estimated_delivery(provider='mock'):
    """Return estimated delivery date based on provider."""
    from datetime import date, timedelta
    days_map = {'ghn': 2, 'ghtk': 3, 'vnpost': 5, 'mock': 3}
    days = days_map.get(provider, 3)
    return date.today() + timedelta(days=days)

import requests
from django.conf import settings


def get_cart(user_id, token=None):
    url = f"{settings.CART_SERVICE_URL}/api/cart/internal/{user_id}/"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None


def clear_cart(user_id):
    url = f"{settings.CART_SERVICE_URL}/api/cart/internal/{user_id}/"
    try:
        requests.delete(url, timeout=5)
    except requests.RequestException:
        pass


def notify_payment_service(order_id, amount, payment_method):
    url = f"{settings.PAYMENT_SERVICE_URL}/api/payments/internal/create/"
    try:
        resp = requests.post(url, json={
            'order_id':       order_id,
            'amount':         str(amount),
            'payment_method': payment_method,
        }, timeout=5)
        if resp.status_code == 201:
            return resp.json()
    except requests.RequestException:
        pass
    return None


def notify_shipping_service(order_id, shipping_address):
    url = f"{settings.SHIPPING_SERVICE_URL}/api/shipping/internal/create/"
    try:
        resp = requests.post(url, json={
            'order_id':        order_id,
            'shipping_address': shipping_address,
        }, timeout=5)
        if resp.status_code == 201:
            return resp.json()
    except requests.RequestException:
        pass
    return None

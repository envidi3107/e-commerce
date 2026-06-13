import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def fetch_product(product_id, token=None):
    """Call product-service to get product details."""
    url = f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/"
    headers = {'Host': 'localhost'}  # Avoid DisallowedHost in product-service
    # Do NOT forward user JWT to product-service. Many services don't share
    # the user DB; forwarding the Authorization header causes remote
    # authentication to fail (401) and breaks simple product lookups.
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        logger.warning(f"fetch_product({product_id}) -> status={resp.status_code}")
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"fetch_product({product_id}) body: {resp.text[:300]}")
    except requests.RequestException as e:
        logger.error(f"fetch_product({product_id}) exception: {e}")
    return None

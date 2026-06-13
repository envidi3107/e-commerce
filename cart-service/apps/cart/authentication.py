"""
Custom JWT authentication for microservices that don't have their own user table.
Decodes the JWT token using the shared secret key and creates a minimal user object
from the token payload (user_id only).
"""
import logging

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class SimpleUser:
    """Minimal user object extracted from JWT payload."""

    def __init__(self, user_id):
        self.id = user_id
        self.pk = user_id
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"User(id={self.id})"


class MicroserviceJWTAuthentication(BaseAuthentication):
    """
    Decode the JWT access token signed by user-service.
    Does NOT hit the database – just reads user_id from the token payload.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.warning(
            "MicroserviceJWTAuthentication: HTTP_AUTHORIZATION=%r method=%s path=%s",
            auth_header[:50] if auth_header else '(empty)',
            request.method,
            request.path,
        )
        if not auth_header.startswith('Bearer '):
            logger.warning("MicroserviceJWTAuthentication: No Bearer prefix, returning None")
            return None

        token = auth_header.split(' ', 1)[1]

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            logger.warning("MicroserviceJWTAuthentication: Token expired")
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            logger.warning("MicroserviceJWTAuthentication: Invalid token: %s", e)
            raise AuthenticationFailed('Invalid token.')

        user_id = payload.get('user_id')
        if user_id is None:
            logger.warning("MicroserviceJWTAuthentication: No user_id in payload: %s", payload)
            raise AuthenticationFailed('Token missing user_id.')

        logger.warning("MicroserviceJWTAuthentication: Authenticated user_id=%s", user_id)
        return (SimpleUser(user_id), token)

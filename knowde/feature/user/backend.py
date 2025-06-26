"""auth backend."""

from __future__ import annotations

from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)

from knowde.config.env import Settings

s = Settings()


def get_strategy() -> JWTStrategy:
    """共通."""
    return JWTStrategy(
        secret=s.KN_AUTH_SECRET,
        lifetime_seconds=s.KN_TOKEN_LIFETIME_SEC,
    )


def get_cookie_transport() -> CookieTransport:
    """For fastapi-users."""
    return CookieTransport(
        cookie_max_age=s.KN_TOKEN_LIFETIME_SEC,
        cookie_secure=s.COOKIE_SECURE,
        cookie_samesite=s.COOKIE_SAMESITE,
        cookie_domain=s.COOKIE_DOMAIN,
    )


def bearer_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="jwt",
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
        get_strategy=get_strategy,
    )


def cookie_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="cookie",
        transport=get_cookie_transport(),
        get_strategy=get_strategy,
    )

import boto3
import jwt
from backend.app.core.logging_config import logger
from botocore.exceptions import ClientError
from cachetools import TTLCache
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app import settings

# ---------------------------------------------------------------------------
# JWKS client — fetches Cognito's public keys once and caches them in-process
# ---------------------------------------------------------------------------

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_uri = (
            f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com"
            f"/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )
        _jwks_client = PyJWKClient(jwks_uri, cache_keys=True)
    return _jwks_client


# ---------------------------------------------------------------------------
# is_premium cache — avoids an AWS call on every request.
# Populated lazily via admin_get_user; TTL = 5 minutes.
# ---------------------------------------------------------------------------

_PREMIUM_TTL = 300  # seconds
_PREMIUM_CACHE_MAX = 1024  # max unique users held in memory
_premium_cache: TTLCache = TTLCache(maxsize=_PREMIUM_CACHE_MAX, ttl=_PREMIUM_TTL)


def _fetch_is_premium(email: str) -> bool:
    """Call Cognito admin_get_user to determine whether the user is premium."""
    if not settings.COGNITO_USER_POOL_ID:
        return False
    try:
        client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)
        response = client.admin_get_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=email,
        )
        attrs = {a["Name"]: a["Value"] for a in response.get("UserAttributes", [])}
        return attrs.get("custom:is_premium", "false").lower() == "true"
    except ClientError as exc:
        logger.warning("premium_fetch_failed", user=email, error=str(exc))
        return False


def _get_is_premium(email: str) -> bool:
    """Return is_premium for *email*, hitting the cache when fresh."""
    if email in _premium_cache:
        return _premium_cache[email]
    is_premium = _fetch_is_premium(email)
    _premium_cache[email] = is_premium
    logger.debug("premium_cache_refreshed", user=email, is_premium=is_premium)
    return is_premium


def invalidate_premium_cache(email: str) -> None:
    """Evict *email* from the premium cache (call after subscription changes)."""
    _premium_cache.pop(email, None)
    logger.info("premium_cache_invalidated", user=email)


# ---------------------------------------------------------------------------
# Token verification — local RS256 check via JWKS, zero AWS calls on hot path
# ---------------------------------------------------------------------------


def verify_access_token(token: str) -> dict:
    """Verify a Cognito access token locally via JWKS.

    Returns ``{"email": str, "is_premium": bool}``.
    Raises HTTP 401 if the token is invalid or expired.
    """
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            # Cognito access tokens have no aud claim
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("auth_token_expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("auth_token_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    if claims.get("token_use") != "access":
        logger.warning("auth_wrong_token_type", token_use=claims.get("token_use"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type — access token required",
        )

    # username = login identifier (email, since username_attributes = ["email"])
    email = claims.get("username") or claims.get("cognito:username", "")
    if not email:
        logger.warning("auth_missing_username_claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing username claim",
        )

    return {"email": email, "is_premium": _get_is_premium(email)}

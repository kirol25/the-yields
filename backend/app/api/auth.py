import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient, PyJWKClientError

from app.core import settings
from app.core.logging_config import logger

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


def verify_token(token: str) -> dict:
    """Verify a Cognito ID token and return `{"email": str, "sub": str}`.

    Raises HTTP 401 if the token is invalid or expired.
    """
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("auth_token_expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("auth_token_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except PyJWKClientError as exc:
        logger.error("auth_jwks_unavailable", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    if claims.get("token_use") != "id":
        logger.warning("auth_wrong_token_type", token_use=claims.get("token_use"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID token required",
        )

    email = claims.get("email", "")
    if not email:
        logger.warning("auth_missing_email_claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing email claim",
        )

    return {
        "email": email,
        "sub": claims.get("sub", ""),
    }

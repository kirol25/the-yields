import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _user_key(request: Request) -> str:
    """Rate-limit key: user sub extracted from ID token, or IP as fallback."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            claims = jwt.decode(
                auth.removeprefix("Bearer "),
                options={"verify_signature": False},
                algorithms=["RS256"],
            )
            sub = claims.get("sub", "")
            if sub:
                return sub
        except Exception:
            pass

    return get_remote_address(request)


limiter = Limiter(key_func=_user_key)

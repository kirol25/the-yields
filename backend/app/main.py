import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import router
from app.core import settings
from app.core.config import description
from app.core.limiter import limiter
from app.core.logging_config import configure_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.version import __version__

# Configure logging before anything else to ensure all logs are captured
configure_logging()

# Disable API docs in production to avoid exposing schema information
_docs_url = "/docs" if settings.docs_enabled else None
_redoc_url = "/redoc" if settings.docs_enabled else None
_openapi_url = "/openapi.json" if settings.docs_enabled else None

# The FastAPI application instance
app = FastAPI(
    title="The Yield API",
    version=__version__,
    description=description,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# Global middleware and exception handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-User-Email"],
)
app.include_router(router)


def main() -> None:
    """Entrypoint for running the API server with Uvicorn."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

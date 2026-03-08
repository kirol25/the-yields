import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import router
from app.config import _description, get_settings
from app.limiter import limiter
from app.logging_config import configure_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.version import __version__

configure_logging()

settings = get_settings()

app = FastAPI(title="The Yield API", version=__version__, description=_description)
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

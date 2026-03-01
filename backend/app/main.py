import uvicorn

from app.version import __version__
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="The Yield API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

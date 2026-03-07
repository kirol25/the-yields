# the-yields — backend

FastAPI service that stores and serves dividend and yield data per year.

## Stack

- **Python 3.13**
- **FastAPI** + **Uvicorn**
- **uv** for dependency management
- **Ruff** for linting and formatting
- Storage: local JSON files or **AWS S3** (configurable)

## Project layout

```md
backend/
├── app/
│   ├── api/
│   │   ├── finance/        # Dividend & yield CRUD routes
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py       # Local file storage
│   │   │   └── s3_repository.py    # S3 storage
│   │   └── monitoring/     # Health check route
│   ├── config.py           # Pydantic settings
│   ├── main.py             # App factory + CORS middleware
│   └── version.py
├── scripts/
│   └── entrypoint.sh
├── Dockerfile
└── pyproject.toml
```

## Running locally

```bash
cd backend
uv run uvicorn app.main:app --reload --port 9002
```

Or via Taskfile from the repo root:

```bash
task api
```

API docs available at `http://localhost:9002/docs`.

## API endpoints

| Method   | Path                              | Description                  |
|----------|-----------------------------------|------------------------------|
| `GET`    | `/api/years`                      | List years with data files   |
| `GET`    | `/api/data/{year}`                | Get dividend + yield data    |
| `PUT`    | `/api/data/{year}`                | Save dividend + yield data   |
| `DELETE` | `/api/data/{year}/{section}/{key}`| Delete a single entry        |
| `GET`    | `/health`                         | Health check                 |

`section` must be `dividends` or `yields`.

## Configuration

All settings are loaded from environment variables (or a `.env` file):

| Variable          | Default                    | Description                          |
|-------------------|----------------------------|--------------------------------------|
| `STORAGE_BACKEND` | `local`                    | `local` or `s3`                      |
| `S3_BUCKET`       | `the-yields-data`           | S3 bucket name (when using s3)       |
| `S3_PREFIX`       | `test-user`                | S3 key prefix (when using s3)        |
| `CORS_ORIGINS`    | `http://localhost:5173`    | Comma-separated allowed origins      |

## Docker

```bash
docker build -t the-yields-backend .
docker run -p 8000:8000 -v $(pwd)/../data:/data -e STORAGE_BACKEND=local the-yields-backend
```

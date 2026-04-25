# the-yields - backend

FastAPI service that stores and serves per-user dividend and yield data.

## Stack

- **Python 3.13**
- **FastAPI** + **Uvicorn**
- **PostgreSQL** via **SQLAlchemy** + **Alembic**
- **uv** for dependency management
- **Ruff** for linting and formatting
- **PyJWT[crypto]** for local RS256 JWT verification (Cognito JWKS)
- **slowapi** for per-user rate limiting

## Project layout

```md
backend/
├── app/
│   ├── api/
│   │   ├── finance/        # Dividend & yield CRUD routes
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── dependencies.py     # Auth context + repo injection
│   │   ├── users/          # User profile routes
│   │   ├── depots/         # Portfolio management
│   │   ├── tickers/        # Ticker management
│   │   ├── feedback/       # SES feedback email
│   │   └── monitoring/     # Health check route
│   ├── core/
│   │   ├── config.py       # Pydantic settings
│   │   ├── logging_config.py
│   │   ├── limiter.py      # slowapi rate limiter (per-user key)
│   │   └── enums.py
│   ├── db/
│   │   ├── models.py       # SQLAlchemy models
│   │   └── session.py      # Database session
│   ├── middleware/
│   │   └── logging.py      # Request logging
│   └── main.py             # App factory, CORS + rate-limit middleware
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/                # Database migrations
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

## Authentication

Every request must include an `Authorization: Bearer <id_token>` header. The ID token is verified locally via Cognito's JWKS endpoint — no AWS call on the hot path.

Returns **503** if `COGNITO_USER_POOL_ID` is not configured, **401** if the token is missing or invalid.

In dev mode (`COGNITO_REGION` unset), the `X-User-Email` header is trusted directly.

## Rate limiting

Write endpoints are rate-limited per user (keyed by `sub` from the ID token, or IP as fallback):

| Endpoint | Limit |
|---|---|
| `PUT /api/data/{year}` | 120/min |
| `PUT /api/settings` | 20/min |
| `DELETE /api/data/{year}/{section}/{key}` | 60/min |
| `POST /api/feedback` | 5/hour |

Exceeded limits return HTTP 429.

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/years` | required | List years with data |
| `GET` | `/api/data/{year}` | required | Get dividend/yield data for a year |
| `PUT` | `/api/data/{year}` | required | Save dividend/yield data |
| `DELETE` | `/api/data` | required | Delete all user data (account deletion) |
| `DELETE` | `/api/data/{year}/{section}/{key}` | required | Delete a single entry |
| `GET` | `/api/settings` | required | Get user settings |
| `PUT` | `/api/settings` | required | Save user settings |
| `POST` | `/api/feedback` | optional | Submit feedback via SES |
| `GET` | `/monitoring/health` | none | Health check |

`section` must be `dividends` or `yields`.

## Configuration

All settings are loaded from environment variables and also from `backend/.env` during local runs:

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `local` | `local` or `prod` — controls doc exposure |
| `DATABASE_URL` | (see .env.example) | PostgreSQL connection string |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `COGNITO_REGION` | `eu-central-1` | AWS region for Cognito JWKS verification |
| `COGNITO_USER_POOL_ID` | — | Cognito User Pool ID |
| `APP_URL` | `http://localhost:5173` | Public frontend URL |
| `AWS_REGION` | `eu-central-1` | AWS region for SES |
| `FEEDBACK_TO_EMAIL` | — | SES recipient for feedback |
| `FEEDBACK_FROM_EMAIL` | — | SES sender for feedback |

## Docker

```bash
docker build -t the-yields-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+psycopg://postgres:postgres@host:5432/the_yields \
  -e COGNITO_REGION=eu-central-1 \
  -e COGNITO_USER_POOL_ID=eu-central-1_xxx \
  the-yields-backend
```

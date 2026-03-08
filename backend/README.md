# the-yields — backend

FastAPI service that stores and serves per-user dividend and yield data.

## Stack

- **Python 3.13**
- **FastAPI** + **Uvicorn**
- **uv** for dependency management
- **Ruff** for linting and formatting
- **PyJWT[crypto]** for local RS256 JWT verification (Cognito JWKS)
- **slowapi** for per-user rate limiting
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
│   │   │   ├── s3_repository.py    # S3 storage
│   │   │   └── dependencies.py     # Auth context + repo injection
│   │   ├── subscription/   # Stripe checkout, portal, webhook
│   │   ├── feedback/       # SES feedback email
│   │   └── monitoring/     # Health check route
│   ├── auth.py             # JWKS-based JWT verification + is_premium cache
│   ├── limiter.py          # slowapi rate limiter (per-user key)
│   ├── config.py           # Pydantic settings
│   ├── main.py             # App factory, CORS + rate-limit middleware
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

## Authentication

**Production** (`COGNITO_REGION` set): every request must include an `Authorization: Bearer <access_token>` header. The token is verified locally via Cognito's JWKS endpoint — no AWS call on the hot path. The `is_premium` flag is resolved from a 5-minute TTL per-user cache backed by `admin_get_user`.

**Dev mode** (`COGNITO_REGION` empty): the `X-User-Email` header is trusted directly after format validation; `is_premium` is always `false`.

## Rate limiting

Write endpoints are rate-limited per user (keyed by email from the JWT, or IP as fallback):

| Endpoint | Limit |
|---|---|
| `PUT /api/data/{year}` | 120/min |
| `PUT /api/settings` | 20/min |
| `DELETE /api/data/{year}/{section}/{key}` | 60/min |
| `POST /api/feedback` | 5/hour |
| `POST /api/subscription/checkout` | 10/min |
| `POST /api/subscription/portal` | 10/min |

Exceeded limits return HTTP 429.

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/years` | required | List years with data (free: current year only) |
| `GET` | `/api/data/{year}` | required | Get dividend/yield data for a year |
| `PUT` | `/api/data/{year}` | required | Save dividend/yield data |
| `DELETE` | `/api/data` | required | Delete all user data (account deletion) |
| `DELETE` | `/api/data/{year}/{section}/{key}` | required | Delete a single entry |
| `GET` | `/api/settings` | required | Get user settings |
| `PUT` | `/api/settings` | required | Save user settings |
| `POST` | `/api/feedback` | optional | Submit feedback via SES |
| `POST` | `/api/subscription/checkout` | required | Create Stripe Checkout session |
| `POST` | `/api/subscription/portal` | required | Create Stripe Billing Portal session |
| `POST` | `/api/subscription/webhook` | Stripe sig | Stripe event receiver |
| `GET` | `/monitoring/health` | none | Health check |

`section` must be `dividends` or `yields`.

## Configuration

All settings are loaded from environment variables (or a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `STORAGE_BACKEND` | `local` | `local` or `s3` |
| `S3_BUCKET` | `the-yields-data` | S3 bucket name |
| `S3_PREFIX` | `test-user` | S3 key prefix |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `COGNITO_REGION` | `` | AWS region (e.g. `eu-central-1`). Empty = dev mode |
| `COGNITO_USER_POOL_ID` | `` | Cognito User Pool ID |
| `STRIPE_SECRET_KEY` | `` | Stripe secret key (`sk_live_...` or `sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | `` | Stripe webhook signing secret (`whsec_...`) |
| `STRIPE_PRICE_ID_MONTHLY` | `` | Stripe Price ID for monthly plan |
| `STRIPE_PRICE_ID_YEARLY` | `` | Stripe Price ID for yearly plan |
| `APP_URL` | `http://localhost:5173` | Public frontend URL (for Stripe redirects) |
| `AWS_REGION` | `eu-central-1` | AWS region for SES |
| `FEEDBACK_TO_EMAIL` | `contact@the-yields.app` | SES recipient for feedback |
| `FEEDBACK_FROM_EMAIL` | `noreply@the-yields.app` | SES sender for feedback |

## Docker

```bash
docker build -t the-yields-backend .
docker run -p 8000:8000 -v $(pwd)/../data:/data \
  -e STORAGE_BACKEND=local \
  -e COGNITO_REGION=eu-central-1 \
  -e COGNITO_USER_POOL_ID=eu-central-1_xxx \
  the-yields-backend
```

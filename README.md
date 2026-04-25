# The Yields

A self-hosted personal finance tracker for dividends and investment yields. Track your dividend income, monitor yields across accounts, and visualize your portfolio performance over time.

![The Yields Dashboard](docs/the-yields.png)

## Features

- **Dividend tracking** — log dividend payments per ticker, per month
- **Yield tracking** — track interest and yield income across accounts
- **Multi-year history** — view and compare data across years
- **Portfolio depots** — organize investments into separate portfolios
- **Dashboard** — charts and summaries of your financial data
- **Multi-language** — English and German (i18n)
- **Self-hosted** — your data stays on your own infrastructure
- **Authentication** — AWS Cognito integration with JWT verification

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | Vue 3, Vite, Pinia, Tailwind CSS   |
| Backend      | FastAPI, SQLAlchemy, Alembic        |
| Database     | PostgreSQL 16                       |
| Auth         | AWS Cognito (JWT)                   |
| Runtime      | Python 3.13, Node 22+              |
| Packaging    | uv (Python), npm (JS)              |
| DevOps       | Docker Compose, GitHub Actions      |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Node.js](https://nodejs.org/) 22+
- [Task](https://taskfile.dev/) (optional)

### Local Development

```bash
# Clone the repo
git clone https://github.com/<owner>/the-yields.git
cd the-yields

# Copy environment files
cp backend/.env.example backend/.env
cp ui/.env.example ui/.env

# Start database, backend, and frontend
task dev
```

| Service  | URL                       |
|----------|---------------------------|
| Frontend | http://localhost:5173     |
| Backend  | http://localhost:9002     |
| API docs | http://localhost:9002/docs |

### Docker

```bash
cp backend/.env.example backend/.env
cp ui/.env.example ui/.env

docker compose up --build
```

| Service  | URL                   |
|----------|-----------------------|
| Frontend | http://localhost:3000 |
| Backend  | http://localhost:8000 |

## Project Structure

```
the-yields/
├── backend/            # FastAPI API server
│   ├── app/
│   │   ├── api/        # Route handlers (finance, users, depots, feedback)
│   │   ├── core/       # Configuration, enums, logging
│   │   ├── db/         # SQLAlchemy models and sessions
│   │   └── middleware/  # Request logging
│   ├── tests/          # Unit and integration tests
│   └── alembic/        # Database migrations
├── ui/                 # Vue 3 SPA
│   ├── src/
│   │   ├── views/      # Page-level components
│   │   ├── components/ # Reusable UI components
│   │   ├── stores/     # Pinia state management
│   │   ├── composables/# Reusable logic
│   │   └── locales/    # i18n (en, de)
│   └── nginx.conf      # Production proxy config
├── infrastructure/     # Terraform and deployment configs
├── docker-compose.yml
└── Taskfile.yml        # Task runner commands
```

## API Endpoints

| Method   | Path                              | Description                         |
|----------|-----------------------------------|-------------------------------------|
| `GET`    | `/api/years`                      | List years with data                |
| `GET`    | `/api/data/{year}`                | Get dividend/yield data for a year  |
| `PUT`    | `/api/data/{year}`                | Save dividend/yield data            |
| `DELETE` | `/api/data`                       | Delete all data for the user        |
| `DELETE` | `/api/data/{year}/{section}/{key}`| Delete a single entry               |
| `GET`    | `/api/settings`                   | Get user settings                   |
| `PUT`    | `/api/settings`                   | Save user settings                  |
| `POST`   | `/api/feedback`                   | Submit feedback (rate limited)      |
| `GET`    | `/monitoring/health`              | Health check                        |

Interactive API docs are available at `/docs` when running locally.

## Configuration

### Backend (`backend/.env`)

| Variable             | Description                                | Default                 |
|----------------------|--------------------------------------------|-------------------------|
| `ENVIRONMENT`        | Deployment environment (`local`, `prod`)   | `local`                 |
| `DATABASE_URL`       | PostgreSQL connection string               | `postgresql+psycopg://postgres:postgres@localhost:5432/the_yields` |
| `COGNITO_REGION`     | AWS Cognito region (empty = dev mode)      | `eu-central-1`          |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID                    | —                       |
| `CORS_ORIGINS`       | Comma-separated allowed origins            | `http://localhost:5173` |
| `FEEDBACK_FROM_EMAIL`| SES verified sender for feedback           | —                       |
| `FEEDBACK_TO_EMAIL`  | Recipient for feedback submissions         | —                       |

### Frontend (`ui/.env`)

| Variable                    | Description                        | Default                  |
|-----------------------------|------------------------------------|--------------------------|
| `VITE_API_BASE`             | Backend URL for dev                | `http://localhost:8000`  |
| `VITE_COGNITO_CLIENT_ID`   | Cognito app client ID              | —                        |
| `VITE_REGISTRATION_ENABLED`| Enable new user registration       | `true`                   |

> **Note:** `VITE_*` variables are compiled into the JS bundle at build time and are visible in the browser. Never put secrets in frontend env vars.

## Authentication

**Production:** Requests must include `Authorization: Bearer <access_token>`. The backend verifies tokens locally via Cognito's JWKS endpoint.

**Dev mode** (`COGNITO_REGION` unset): The `X-User-Email` header is trusted directly — no token required.

## Data Format

Year data is stored per user in PostgreSQL and follows this structure:

```json
{
  "dividends": {
    "AAPL": { "name": "Apple Inc.", "months": { "01": 1.50 } }
  },
  "yields": {
    "Chase": { "months": { "01": 25.00 } }
  }
}
```

## Task Commands

| Task           | Description                            |
|----------------|----------------------------------------|
| `task dev`     | Start database, UI, and API            |
| `task ui`      | Start the Vite dev server              |
| `task api`     | Start the FastAPI server               |
| `task db`      | Start the PostgreSQL container         |
| `task test`    | Run backend tests                      |
| `task format`  | Run Ruff + Prettier via pre-commit     |
| `task build`   | Build both UI and backend              |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)

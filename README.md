# the-yield

A personal finance tracker for dividends and investment yields. Built with a FastAPI backend and a Vue 3 frontend.

## Structure

```md
the-yield/
├── backend/        # FastAPI API server
├── ui/             # Vue 3 SPA
├── data/           # JSON data files (YYYY.json), mounted as a volume in Docker
├── docker-compose.yml
└── Taskfile.yml
```

## Quick start

### Local development

Requires [uv](https://github.com/astral-sh/uv) and Node 22+.

```bash
# Start both servers concurrently
task dev
```

| Service  | URL                      |
|----------|--------------------------|
| Frontend | http://localhost:5173    |
| Backend  | http://localhost:9002    |
| API docs | http://localhost:9002/docs |

### Docker

```bash
# Copy and fill in the UI env file first
cp ui/.env.example ui/.env

docker compose up --build
```

| Service  | URL                   |
|----------|-----------------------|
| Frontend | http://localhost      |
| Backend  | http://localhost:8000 |

## Data format

Year data is stored per user under `data/{user_email}/YYYY.json` (local) or `s3://{bucket}/{prefix}/{user_email}/YYYY.json` (S3):

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

## API endpoints

All requests require an `X-User-Email` header identifying the authenticated user.

| Method   | Path                              | Description                          |
|----------|-----------------------------------|--------------------------------------|
| `GET`    | `/api/years`                      | List years with data                 |
| `GET`    | `/api/data/{year}`                | Get dividend/yield data for a year   |
| `PUT`    | `/api/data/{year}`                | Save dividend/yield data for a year  |
| `DELETE` | `/api/data`                       | Delete **all** data for the user (account deletion) |
| `DELETE` | `/api/data/{year}/{section}/{key}`| Delete a single entry                |

Interactive docs available at `http://localhost:9002/docs`.

## Account deletion

When a user deletes their account the frontend:
1. Calls `DELETE /api/data` to wipe all their data from the backend
2. Calls Cognito `DeleteUser` to remove the auth account
3. Clears local tokens and redirects to `/login`

## Taskfile commands

| Task            | Description                              |
|-----------------|------------------------------------------|
| `task dev`      | Start both UI and API concurrently       |
| `task ui`       | Start the Vite dev server on :5173       |
| `task api`      | Start the FastAPI server on :9002        |
| `task format`   | Run Ruff + Prettier via pre-commit       |

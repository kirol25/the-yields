# the-yields

[![CI](https://github.com/kirol25/the-yields/actions/workflows/ci.yml/badge.svg)](https://github.com/kirol25/the-yields/actions/workflows/ci.yml)
[![Dependabot Updates](https://github.com/kirol25/the-yields/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/kirol25/the-yields/actions/workflows/dependabot/dependabot-updates)

A personal finance tracker for dividends and investment yields. Built with a FastAPI backend and a Vue 3 frontend.

## Structure

```md
the-yields/
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

## Frontend ↔ Backend communication

### Local development

In dev mode, Vite's built-in proxy handles `/api/*` requests:

```md
Browser → Vite dev server (:5173) → FastAPI (:9002)
```

`vite.config.js` proxies any `/api/` request to `http://localhost:9002`, so the browser never needs to know the backend port.

### Production (Docker)

In production the frontend is compiled into static files and served by nginx inside the `ui` container. API calls use **relative paths** (e.g. `/api/years`), which the browser sends back to the same origin that served the page. nginx inside the container catches them:

```
Browser → nginx in ui container (:80)
            ├── /         → serve static files
            └── /api/*    → proxy_pass http://backend:8000 (Docker internal DNS)
                                └── backend container (:8000)
```

`backend` in `proxy_pass` resolves via Docker Compose's internal DNS to the `backend` service - not the container name (`the-yields-backend-1`). The backend port is bound to `127.0.0.1:8000` on the host and is not directly reachable from the internet; only nginx can reach it through the Docker network.

### `VITE_API_BASE` and why it must be empty in production

`ui/src/config.js` exports `API_BASE = import.meta.env.VITE_API_BASE`. All fetch/axios calls prepend this to their paths:

```js
axios.get(`${API_BASE}/api/years`)
```

- **Dev**: set to `http://localhost:9002` so calls go directly to FastAPI
- **Production**: must be `""` (empty string) so calls become relative (e.g. `/api/years`) and are caught by nginx

Any `VITE_*` variable is compiled into the JS bundle at build time and is readable by anyone in DevTools - never put secrets there. `VITE_COGNITO_CLIENT_ID` is safe because the Cognito Client ID is a public identifier by design.

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

## Authentication

**Production**: requests must include `Authorization: Bearer <access_token>`. The backend verifies tokens locally via Cognito's JWKS endpoint (no AWS call on the hot path). The `is_premium` flag is cached per user for 5 minutes.

**Dev mode** (`COGNITO_REGION` unset): the `X-User-Email` header is trusted directly; `is_premium` is always `false`.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/years` | List years with data (free: current year only) |
| `GET` | `/api/data/{year}` | Get dividend/yield data for a year |
| `PUT` | `/api/data/{year}` | Save dividend/yield data |
| `DELETE` | `/api/data` | Delete **all** data for the user (account deletion) |
| `DELETE` | `/api/data/{year}/{section}/{key}` | Delete a single entry |
| `GET` | `/api/settings` | Get user settings |
| `PUT` | `/api/settings` | Save user settings |
| `POST` | `/api/feedback` | Submit feedback via SES (5/hour limit) |
| `POST` | `/api/subscription/checkout` | Create Stripe Checkout session |
| `POST` | `/api/subscription/portal` | Create Stripe Billing Portal session |
| `POST` | `/api/subscription/webhook` | Stripe webhook receiver |
| `GET` | `/monitoring/health` | Health check |

Interactive docs available at `http://localhost:9002/docs`.

## Stripe setup

### 1. Create products & prices

1. Go to **dashboard.stripe.com → Products → Add product**
2. Create a product called e.g. **"The Yields Premium"**
3. Under **Pricing**, add two recurring prices:
   - **Monthly**: e.g. €4.99/month → copy the `price_...` ID
   - **Yearly**: e.g. €39.99/year → copy the `price_...` ID

> **Important**: Use the `price_...` IDs, not the `prod_...` product IDs.

### 2. Create a webhook endpoint

1. Go to **Developers → Webhooks → Add endpoint**
2. Set the endpoint URL to `https://<your-domain>/api/subscription/webhook`
3. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `customer.subscription.paused`
   - `invoice.payment_failed`
4. Save and copy the **Signing secret** (`whsec_...`)

### 3. Configure environment variables

Add to `backend/.env`:

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_YEARLY=price_...
APP_URL=https://your-domain.com
```

Add to `ui/.env`:

```env
VITE_STRIPE_ENABLED=true
```

### 4. Test webhooks locally

Install the [Stripe CLI](https://stripe.com/docs/stripe-cli) and forward events to your local backend:

```bash
brew install stripe/stripe-cli/stripe
stripe login
stripe listen --forward-to localhost:9002/api/subscription/webhook
```

The CLI prints a local `whsec_...` secret — use that as `STRIPE_WEBHOOK_SECRET` when developing locally (it differs from the dashboard webhook secret).

### 5. Subscription lifecycle

| Event | When it fires | Effect |
| --- | --- | --- |
| `checkout.session.completed` | User completes payment | `is_premium = True` |
| `customer.subscription.deleted` | Paid period expires | `is_premium = False` |
| `customer.subscription.paused` | Subscription paused | `is_premium = False` |
| `invoice.payment_failed` | Payment fails | Logged only (no action) |

**Cancellation behaviour**: when a user cancels via the billing portal, Stripe sets `cancel_at_period_end: true` but the subscription stays active — no webhook fires immediately. The user keeps premium access until the end of the paid period, at which point `customer.subscription.deleted` fires and `is_premium` is set to `False`.

> **Production note**: the `customer.subscription.deleted` event is delivered by Stripe on the period end date — make sure your production webhook endpoint is live and reachable, otherwise access will not be revoked on time.

## Account deletion

When a user deletes their account the frontend:

1. Calls `DELETE /api/data` to wipe all their data from the backend
2. Calls Cognito `DeleteUser` to remove the auth account
3. Clears local tokens and redirects to `/login`

## Deployment (Ansible)

Before running Ansible for the first time, copy your SSH key to the server:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@0.0.0.0
```

Then provision and deploy:

```bash
cd ansible
ansible-playbook playbooks/setup.yml   # first time only
ansible-playbook playbooks/deploy.yml  # subsequent deploys
```

## Taskfile commands

| Task            | Description                              |
|-----------------|------------------------------------------|
| `task dev`      | Start both UI and API concurrently       |
| `task ui`       | Start the Vite dev server on :5173       |
| `task api`      | Start the FastAPI server on :9002        |
| `task format`   | Run Ruff + Prettier via pre-commit       |

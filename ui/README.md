# the-yields — ui

Vue 3 single-page application for tracking dividends and investment yields.

## Stack

- **Vue 3** (Composition API + `<script setup>`)
- **Vite 6**
- **Pinia** — state management
- **Vue Router 4**
- **vue-i18n 11** — i18n (default language: German)
- **Tailwind CSS v4** via `@tailwindcss/vite`
- **Chart.js** via `vue-chartjs`
- **Axios** for API calls

## Project layout

```
ui/
├── src/
│   ├── views/              # Page components
│   │   ├── Landing.vue
│   │   ├── Dashboard.vue
│   │   ├── Dividends.vue
│   │   ├── Yields.vue
│   │   ├── Profile.vue
│   │   └── Settings.vue
│   ├── components/         # Shared components
│   ├── stores/             # Pinia stores
│   │   ├── authStore.js
│   │   ├── dataStore.js
│   │   ├── settingsStore.js
│   │   └── toastStore.js
│   ├── composables/        # Reusable composables
│   ├── locales/            # i18n translation files
│   │   ├── en.json
│   │   └── de.json
│   ├── router/
│   ├── i18n.js
│   └── style.css           # Tailwind entry (@import "tailwindcss")
├── scripts/
│   └── entrypoint.sh
├── nginx.conf              # Served in production via nginx
├── Dockerfile
└── vite.config.js
```

## Running locally

```bash
cd ui
npm install
npm run dev
```

Or via Taskfile from the repo root:

```bash
task ui
```

Vite dev server starts on http://localhost:5173 and proxies `/api` requests to the backend at `http://localhost:8000`.

## Environment variables

Create a `.env` file in `ui/` for local overrides:

| Variable                | Description                             |
|-------------------------|-----------------------------------------|
| `VITE_API_BASE`         | API base URL (empty = same origin)      |
| `VITE_COGNITO_REGION`   | AWS Cognito region                      |
| `VITE_COGNITO_CLIENT_ID`| AWS Cognito app client ID               |

## i18n

- Locale is persisted in `localStorage` via `settingsStore`.
- Switch locale programmatically: `settingsStore.setLocale('en')`.
- Add translations to `src/locales/en.json` and `src/locales/de.json`.

## Build

```bash
npm run build   # outputs to dist/
npm run preview # preview the production build
```

## nginx (production)

The production image serves the built SPA via nginx (`nginx.conf`).

**Caching**
- `index.html` — `no-cache, must-revalidate`: always revalidated so new deploys are picked up immediately.
- `/assets/*` — `max-age=31536000, immutable`: cached for 1 year. Safe because Vite hashes asset filenames on every build.

**Rate limiting**
- `/api/` is limited to 10 req/s per IP with a burst of 20. Requests beyond the burst receive a `429 Too Many Requests` response.

## Docker

```bash
docker build \
  --build-arg VITE_COGNITO_REGION=eu-central-1 \
  --build-arg VITE_COGNITO_CLIENT_ID=<client-id> \
  -t the-yields-ui .

docker run -p 80:80 the-yields-ui
```

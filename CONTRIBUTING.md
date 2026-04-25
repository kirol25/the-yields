# Contributing to The Yields

Thanks for your interest in contributing! This guide will help you get started.

## Reporting Bugs

Open a [GitHub Issue](../../issues/new) with:

- A clear title describing the problem
- Steps to reproduce the bug
- Expected vs. actual behavior
- Your environment (OS, browser, Python/Node versions)

## Suggesting Features

Open an issue with the **feature request** label. Describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Node.js](https://nodejs.org/) 22+
- [Task](https://taskfile.dev/) (optional, for task runner commands)

### Getting Started

```bash
# Clone the repo
git clone https://github.com/<owner>/the-yields.git
cd the-yields

# Copy environment files
cp backend/.env.example backend/.env
cp ui/.env.example ui/.env

# Start the database
docker compose up db -d

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Start both servers
task dev
```

The frontend runs at `http://localhost:5173` and the backend at `http://localhost:9002`.

## Code Style

### Python (backend)

- Formatter and linter: [Ruff](https://docs.astral.sh/ruff/)
- Pre-commit hooks run Ruff automatically on staged files
- Run manually: `pre-commit run --all-files`

### JavaScript/Vue (frontend)

- Formatter: [Prettier](https://prettier.io/)
- Follow the existing Vue 3 Composition API patterns

## Running Tests

```bash
# Backend unit tests
cd backend && uv run pytest tests/unit

# Backend integration tests (requires running database)
cd backend && uv run pytest tests/integration

# Frontend build check
cd ui && npm run build
```

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make small, focused commits** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add dividend export to CSV
   fix: correct monthly total calculation
   docs: update API endpoint table
   refactor: simplify year filtering logic
   test: add unit tests for yield calculator
   chore: update dependencies
   ```

3. **Ensure your changes pass**:
   - Pre-commit hooks (formatting, linting)
   - Existing tests still pass
   - Add tests for new functionality

4. **Open a PR** against `main` with:
   - A clear title following conventional commit format
   - A description of what changed and why
   - Screenshots for UI changes

5. A maintainer will review your PR. Please be patient and address any feedback.

## Project Structure

```
the-yields/
├── backend/          # FastAPI API server
│   ├── app/          # Application code
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Configuration, enums
│   │   ├── db/       # SQLAlchemy models, sessions
│   │   └── middleware/
│   ├── tests/        # Unit and integration tests
│   └── alembic/      # Database migrations
├── ui/               # Vue 3 SPA
│   ├── src/
│   │   ├── views/    # Page components
│   │   ├── components/
│   │   ├── stores/   # Pinia state management
│   │   ├── composables/
│   │   └── locales/  # i18n translations
│   └── public/
└── docker-compose.yml
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

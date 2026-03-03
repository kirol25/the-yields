FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app/ ./app/
COPY scripts/entrypoint.sh ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

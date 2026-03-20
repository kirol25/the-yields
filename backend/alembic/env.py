import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Ensure the backend package root is on sys.path so app.* imports work
# when Alembic is invoked from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Import Base and all models so their metadata is populated before
# Alembic inspects it for autogenerate.
from app.core.config import get_settings  # noqa: E402
from app.db import models  # noqa: E402, F401
from app.db.base import Base  # noqa: E402

# Alembic Config object — gives access to alembic.ini values.
config = context.config

# Wire up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the database URL from application settings so we never
# hard-code credentials in alembic.ini.
_settings = get_settings()
config.set_main_option("sqlalchemy.url", _settings.DATABASE_URL)

# Metadata to diff against for autogenerate migrations.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emit SQL to stdout)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

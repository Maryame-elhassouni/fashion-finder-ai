from logging.config import fileConfig
from pathlib import Path
import os

from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# =====================================================
# 🔥 LOAD ENV FIRST
# =====================================================
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# =====================================================
# ALEMBIC CONFIG
# =====================================================
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =====================================================
# IMPORT YOUR MODELS (IMPORTANT)
# =====================================================
from backend.app.core.database import Base
import backend.app.models  # MUST import all models via __init__.py

# Optional explicit imports (safe fallback)
from backend.app.models.category import Category
from backend.app.models.article import Article
from backend.app.models.user import User
from backend.app.models.search_history import SearchHistory

target_metadata = Base.metadata

# =====================================================
# OFFLINE MIGRATION
# =====================================================
def run_migrations_offline() -> None:
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

# =====================================================
# ONLINE MIGRATION
# =====================================================
def run_migrations_online() -> None:
    # IMPORTANT: ensure we use correct DB URL
    db_url = config.get_main_option("sqlalchemy.url")

    connectable = engine_from_config(
        {"sqlalchemy.url": db_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True if "sqlite" in db_url else False,
        )

        with context.begin_transaction():
            context.run_migrations()

# =====================================================
# RUN
# =====================================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
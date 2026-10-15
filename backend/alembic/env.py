from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, text

from app import models  # noqa: F401  (registers the tables on Base)
from app.config import DATABASE_URL
from app.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


# any fixed number works, every replica just has to use the same one
MIGRATION_LOCK_ID = 727274


def run_migrations_online() -> None:
    engine = create_engine(DATABASE_URL)
    is_postgres = engine.dialect.name == "postgresql"
    # Several backend pods can start at once. On PostgreSQL they take turns
    # so two pods never try to create the same table.
    lock_conn = engine.connect() if is_postgres else None
    try:
        if lock_conn is not None:
            lock_conn.execute(text("SELECT pg_advisory_lock(:id)"), {"id": MIGRATION_LOCK_ID})
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        if lock_conn is not None:
            lock_conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": MIGRATION_LOCK_ID})
            lock_conn.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

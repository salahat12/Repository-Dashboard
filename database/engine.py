import os
from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import OrmBase

# Import all models so SQLAlchemy registers their tables
from models import (
    Repository,
    Contributor,
    Branch,
    PullRequest,
    Commit,
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:{os.getenv('PG_PASSWORD')}@localhost:5432/postgres",
)


# Create the connection to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    future=True,
)


# Create database sessions
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    future=True,
)


# Prevent creating the schema multiple times
_schema_ready = False
_schema_lock = Lock()


def ensure_schema() -> None:
    global _schema_ready

    # If tables were already created, do nothing
    if _schema_ready:
        return

    # Prevent multiple threads from creating tables simultaneously
    with _schema_lock:

        if _schema_ready:
            return

        # Create all tables registered with OrmBase
        OrmBase.metadata.create_all(
            bind=engine,
            checkfirst=True,
        )

        _schema_ready = True


@contextmanager
def session_scope() -> Iterator[Session]:

    # Make sure the database tables exist
    ensure_schema()

    # Create a database session
    session = SessionLocal()

    try:
        yield session

        # Save changes
        session.commit()

    except Exception:
        # Undo changes if an error happens
        session.rollback()
        raise

    finally:
        # Always close the database connection
        session.close()
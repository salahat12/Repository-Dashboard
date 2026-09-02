"""
Database engine, session management, and schema creation for the
Repository Dashboard.

This module is the bridge between the application and PostgreSQL.  It
does three things:

1. Builds a SQLAlchemy engine connected to the database (the URL comes
   from the ``DATABASE_URL`` environment variable, falling back to a
   local ``postgres`` database using the ``PG_PASSWORD`` from ``.env``).

2. Provides a ``session_scope()`` context manager that yields an
   SQLAlchemy ``Session``.  The context manager:
   - ensures the database schema exists (creates tables if missing),
   - commits on success,
   - rolls back on any exception,
   - always closes the connection when done.
   Writers and readers use ``with session_scope() as session:`` so they
   never have to think about commit/rollback/close.

3. Creates the database schema on first use via ``ensure_schema()``.
   It calls ``OrmBase.metadata.create_all(checkfirst=True)`` which
   creates every table defined in ``models`` if it does not already
   exist.  This means **no manual SQL is needed** — tables appear
   automatically the first time the server handles a request.

Conventions
-----------
* The engine uses a connection pool (``pool_size=5``, ``max_overflow=10``)
  so concurrent requests reuse connections instead of opening a new one
  each time.
* ``pool_pre_ping=True`` verifies the connection is still alive before
  using it (handles PostgreSQL restarts gracefully).
* ``expire_on_commit=False`` lets code read attributes from objects
  after a commit without triggering a lazy-load (avoids surprises in
  the reader when it accesses related objects).
"""

import os
from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import OrmBase

load_dotenv()
# Import all models so SQLAlchemy registers their tables.
# If a model is not imported here, its table will not be created by
# ``ensure_schema()`` and will be missing from the database.


# Database connection URL.
# Format: postgresql+psycopg2://user:password@host:port/database
# Falls back to a local PostgreSQL instance using PG_PASSWORD from .env.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:{os.getenv('PG_PASSWORD')}@localhost:5432/postgres",
)


# ---------------------------------------------------------------------------
# Engine — owns the connection pool to PostgreSQL
# ---------------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # keep up to 5 connections open
    max_overflow=10,       # allow up to 10 more under load
    pool_pre_ping=True,    # verify connection is alive before using it
    future=True,           # use SQLAlchemy 2.0 behaviour
)


# ---------------------------------------------------------------------------
# Session factory — produces new Session objects bound to the engine
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    future=True,
)


# ---------------------------------------------------------------------------
# Schema creation — idempotent, thread-safe
# ---------------------------------------------------------------------------
_schema_ready = False
_schema_lock = Lock()


def ensure_schema() -> None:
    """Create all tables defined in ``models`` if they do not exist.

    This is safe to call many times — it is a no-op after the first
    successful call.  Thread-safety is provided by a lock so that two
    concurrent requests do not race to create tables.
    """
    global _schema_ready

    if _schema_ready:
        return

    with _schema_lock:
        if _schema_ready:
            return

        # create_all(checkfirst=True) only creates tables that are missing.
        OrmBase.metadata.create_all(
            bind=engine,
            checkfirst=True,
        )

        _schema_ready = True


# ---------------------------------------------------------------------------
# Session scope — the standard way to get a database session
# ---------------------------------------------------------------------------
@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a SQLAlchemy Session with automatic commit/rollback/close.

    Usage::

        with session_scope() as session:
            user = session.get(User, 1)
            user.name = "new name"
            # commit happens automatically here

    If any exception escapes the ``with`` block, the transaction is
    rolled back and the exception is re-raised.  The session is always
    closed in the ``finally`` block.
    """
    ensure_schema()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

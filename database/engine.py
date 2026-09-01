import os
from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import OrmBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:{os.getenv('PG_PASSWORD')}@localhost:5432/postgres",
)

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

_schema_ready = False
_schema_lock = Lock()


def ensure_schema() -> None:

    global _schema_ready

    if _schema_ready:
        return

    with _schema_lock:
        if _schema_ready:
            return

        OrmBase.metadata.create_all(engine, checkfirst=True)

        _schema_ready = True


@contextmanager
def session_scope() -> Iterator[Session]:

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
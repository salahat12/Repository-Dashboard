import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base


# Create database engine
DATABASE_URL = f"postgresql://postgres:{os.getenv('PG_PASSWORD', 'Sama@9875123')}@localhost:5432/postgres"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


# Enable foreign keys for SQLite (if needed)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

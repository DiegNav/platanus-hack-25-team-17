"""Helper functions for database operations."""

from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.config import settings


@contextmanager
def get_sync_session():
    """Get a synchronous database session.
    
    This function creates a synchronous session from the database URL.
    It's used for SQL functions that require synchronous sessions.
    
    Yields:
        Session: Synchronous database session
    """
    # Convert async URL to sync URL
    database_url = str(settings.DATABASE_URL)
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif database_url.startswith("postgresql://"):
        pass  # Already sync URL
    
    engine = create_engine(database_url, echo=settings.DB_ECHO)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


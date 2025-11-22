"""
Database configuration and session management for SQLAlchemy.
Supports both in-memory SQLite for testing and MySQL for production.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# SQLAlchemy Base for all models
Base = declarative_base()

# Database URL configuration
DB_USER = os.environ.get("DB_USER", "ms1_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password123")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "ms1_db")
USE_SQLITE = os.environ.get("USE_SQLITE", "False").lower() == "true"

if USE_SQLITE:
    # For development/testing: SQLite in memory
    DATABASE_URL = "sqlite:///:memory:"
else:
    # For production: MySQL
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.environ.get("SQL_ECHO", "False").lower() == "true",
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency for FastAPI to get database session.
    Usage in route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables. Use with caution!
    """
    Base.metadata.drop_all(bind=engine)

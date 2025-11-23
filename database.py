"""
Database configuration and session management for SQLAlchemy.
Supports both in-memory SQLite for testing and MySQL for production.

Cloud Run Configuration:
  Set these environment variables in Cloud Run:
  - DB_HOST: Cloud SQL proxy socket or IP address
  - DB_USER: MySQL user (e.g., ms1_user)
  - DB_PASSWORD: MySQL password
  - DB_PORT: MySQL port (default: 3306)
  - DB_NAME: Database name (default: ms1_db)
  
  Example (Cloud SQL with Cloud Run):
    DB_HOST=ms1-db
    DB_USER=ms1_user
    DB_PASSWORD=your_secure_password
    DB_PORT=3306
    DB_NAME=ms1_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
Base = declarative_base()

# Database URL configuration
DB_USER = os.environ.get("DB_USER", "ms1_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password123")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "ms1_db")
USE_SQLITE = os.environ.get("USE_SQLITE", "False").lower() == "true"

# Log configuration for debugging
if not USE_SQLITE:
    logger.info(f"Database config: {DB_HOST}:{DB_PORT}/{DB_NAME} (user: {DB_USER})")

if USE_SQLITE:
    # For development/testing: SQLite in memory
    DATABASE_URL = "sqlite:///:memory:"
    logger.info("Using SQLite in-memory database")
    # SQLite doesn't support pool settings, use minimal config
    engine = create_engine(
        DATABASE_URL,
        echo=os.environ.get("SQL_ECHO", "False").lower() == "true",
        connect_args={"check_same_thread": False},
    )
else:
    # For production: MySQL
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"Using MySQL database at {DB_HOST}:{DB_PORT}")
    # Create engine with optimized settings for Cloud Run
    engine = create_engine(
        DATABASE_URL,
        echo=os.environ.get("SQL_ECHO", "False").lower() == "true",
        pool_pre_ping=True,              # Test connections before using them
        pool_recycle=3600,               # Recycle connections after 1 hour
        pool_size=5,                      # Reduced for Cloud Run (stateless)
        max_overflow=10,                  # Allow overflow connections
        connect_args={"timeout": 10},     # Connection timeout for reliability
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

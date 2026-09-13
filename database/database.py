"""
NEXUS AI Agent - Database Connection & Engine Setup
Configures SQLite database connection using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from utils.logger import logger

# Create SQLite SQLAlchemy Engine
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initializes all database tables created via SQLAlchemy models."""
    try:
        from database import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise e

def get_db():
    """FastAPI & Service dependency for DB session context management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
NEXUS AI Agent - Database Connection & Engine Setup
Configures SQLite database connection using SQLAlchemy with auto-migration support.
"""

from sqlalchemy import create_engine, inspect, text
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
    """Initializes all database tables created via SQLAlchemy models and performs automatic schema migration."""
    try:
        from database import models  # noqa: F401
        Base.metadata.create_all(bind=engine)

        # Auto-migrate missing columns for existing SQLite database files
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "users" in tables:
            columns = [c["name"] for c in inspector.get_columns("users")]
            with engine.begin() as conn:
                if "auth_id" not in columns:
                    logger.info("Migrating schema: Adding 'auth_id' to 'users' table")
                    conn.execute(text("ALTER TABLE users ADD COLUMN auth_id VARCHAR(100)"))
                if "email" not in columns:
                    logger.info("Migrating schema: Adding 'email' to 'users' table")
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
                if "password_hash" not in columns:
                    logger.info("Migrating schema: Adding 'password_hash' to 'users' table")
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                if "auth_provider" not in columns:
                    logger.info("Migrating schema: Adding 'auth_provider' to 'users' table")
                    conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'email'"))
                if "is_email_verified" not in columns:
                    logger.info("Migrating schema: Adding 'is_email_verified' to 'users' table")
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN DEFAULT 0"))

        logger.info("Database tables and schema auto-migrations initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables/migrations: {e}")

def get_db():
    """FastAPI & Service dependency for DB session context management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

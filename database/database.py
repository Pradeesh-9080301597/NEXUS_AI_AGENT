"""
NEXUS AI Agent - Database Connection & Engine Setup
Configures SQLite database connection using SQLAlchemy with auto-migration support.
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
try:
    from config import settings
    from utils.logger import logger
except ImportError:
    try:
        from ..config import settings
        from ..utils.logger import logger
    except Exception:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
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

        # Robust Auto-Migration: Add any missing column for existing tables in SQLite
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Map of table_name -> dict of column_name: column_type_sql
        migration_rules = {
            "users": {
                "auth_id": "VARCHAR(100)",
                "email": "VARCHAR(255)",
                "password_hash": "VARCHAR(255)",
                "auth_provider": "VARCHAR(50) DEFAULT 'email'",
                "is_email_verified": "BOOLEAN DEFAULT 0",
            },
            "profiles": {
                "full_name": "VARCHAR(100)",
                "avatar_url": "VARCHAR(255)",
                "college": "VARCHAR(200)",
                "degree": "VARCHAR(150)",
                "department": "VARCHAR(150)",
                "current_year": "VARCHAR(50)",
                "graduation_year": "VARCHAR(50)",
                "secondary_career": "VARCHAR(100)",
                "preferred_domain": "VARCHAR(100)",
                "daily_learning_hours": "FLOAT DEFAULT 2.0",
                "learning_preference": "VARCHAR(100) DEFAULT 'Hands-on Projects'",
                "company_preference": "VARCHAR(100) DEFAULT 'Product Startups'",
                "location_preference": "VARCHAR(100) DEFAULT 'Remote / Hybrid'",
            },
            "career_goals": {
                "secondary_role": "VARCHAR(100)",
                "timeframe_months": "INTEGER DEFAULT 6",
                "target_salary_tier": "VARCHAR(50)",
            },
            "user_skills": {
                "confidence_score": "FLOAT DEFAULT 70.0",
                "status": "VARCHAR(50) DEFAULT 'MASTERED'",
                "evidence_json": "TEXT",
            },
            "roadmaps": {
                "readiness_score": "FLOAT DEFAULT 0.0",
            },
            "roadmap_items": {
                "phase_name": "VARCHAR(100) DEFAULT 'Core Capability Phase'",
                "objectives": "TEXT",
                "duration": "VARCHAR(100) DEFAULT '4 Weeks'",
                "practice_tasks": "TEXT",
            },
            "user_progress": {
                "verified_by_ai": "BOOLEAN DEFAULT 0",
            },
            "project_recommendations": {
                "match_score": "FLOAT DEFAULT 85.0",
                "required_skills": "VARCHAR(255)",
                "outcome": "TEXT",
                "status": "VARCHAR(50) DEFAULT 'RECOMMENDED'",
            },
            "resumes": {
                "file_name": "VARCHAR(255)",
                "raw_text": "TEXT",
                "extracted_skills_json": "TEXT",
                "score_percentage": "FLOAT DEFAULT 0.0",
                "feedback_json": "TEXT",
            },
            "job_descriptions": {
                "extracted_reqs_json": "TEXT",
                "match_percentage": "FLOAT DEFAULT 0.0",
                "gap_analysis_json": "TEXT",
            },
            "assessment_results": {
                "assessment_type": "VARCHAR(100) DEFAULT 'Technical'",
                "skill_name": "VARCHAR(100)",
                "score_percentage": "FLOAT DEFAULT 0.0",
                "feedback": "TEXT",
            }
        }

        with engine.begin() as conn:
            for table_name, columns_spec in migration_rules.items():
                if table_name in tables:
                    existing_cols = [c["name"] for c in inspector.get_columns(table_name)]
                    for col_name, col_type in columns_spec.items():
                        if col_name not in existing_cols:
                            logger.info(f"Auto-migrating {table_name}: Adding column {col_name}")
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))

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

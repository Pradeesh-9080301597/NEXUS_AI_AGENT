"""
Database module for NEXUS AI Agent.
Exposes database connection helpers and all normalized ORM entities.
"""

from database.database import Base, SessionLocal, init_db, engine
from database.models import (
    User,
    Profile,
    CareerGoal,
    UserSkill,
    Roadmap,
    RoadmapItem,
    UserProgress,
    ProjectRecommendation,
    Resume,
    JobDescription,
    AssessmentResult,
)

__all__ = [
    "Base",
    "SessionLocal",
    "init_db",
    "engine",
    "User",
    "Profile",
    "CareerGoal",
    "UserSkill",
    "Roadmap",
    "RoadmapItem",
    "UserProgress",
    "ProjectRecommendation",
    "Resume",
    "JobDescription",
    "AssessmentResult",
]

"""
NEXUS AI Agent - SQLAlchemy Database Models
Defines tables for USERS, USER_SKILLS, CAREER_GOALS, ROADMAPS, ROADMAP_ITEMS, USER_PROGRESS, and PROJECT_RECOMMENDATIONS.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    """Stores main user profile information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    education = Column(String(200), nullable=True)
    experience_level = Column(String(50), default="Beginner")  # Beginner, Intermediate, Advanced
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    progress_entries = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("ProjectRecommendation", back_populates="user", cascade="all, delete-orphan")


class CareerGoal(Base):
    """Stores user target career path and timeline goals."""
    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(100), nullable=False)  # e.g., AI Engineer, Full Stack Developer
    timeframe_months = Column(Integer, default=6)
    target_salary_tier = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="career_goals")
    roadmaps = relationship("Roadmap", back_populates="career_goal", cascade="all, delete-orphan")


class UserSkill(Base):
    """Stores individual skills associated with a user and their status classification."""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50), default="Beginner")  # Beginner, Intermediate, Advanced
    status = Column(String(50), default="COMPLETED")  # COMPLETED, IN_PROGRESS, MISSING, OPTIONAL

    user = relationship("User", back_populates="skills")


class Roadmap(Base):
    """Stores generated learning roadmap container for a user."""
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_goal_id = Column(Integer, ForeignKey("career_goals.id"), nullable=True)
    total_months = Column(Integer, default=6)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roadmaps")
    career_goal = relationship("CareerGoal", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapItem(Base):
    """Stores monthly learning module/topic details within a roadmap."""
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    month_number = Column(Integer, nullable=False)
    topic_name = Column(String(150), nullable=False)
    objectives = Column(Text, nullable=True)
    duration = Column(String(100), default="4 Weeks")
    practice_tasks = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED

    roadmap = relationship("Roadmap", back_populates="items")


class UserProgress(Base):
    """Stores completed topics and learning milestone updates."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_completed = Column(String(150), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="progress_entries")


class ProjectRecommendation(Base):
    """Stores recommended hands-on projects suited for the user's skill level."""
    __tablename__ = "project_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(50), default="BEGINNER")  # BEGINNER, INTERMEDIATE, ADVANCED
    required_skills = Column(String(255), nullable=True)
    status = Column(String(50), default="RECOMMENDED")  # RECOMMENDED, IN_PROGRESS, COMPLETED

    user = relationship("User", back_populates="projects")

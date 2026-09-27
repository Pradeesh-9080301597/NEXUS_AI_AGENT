"""
NEXUS AI 2.0 - SQLAlchemy Database Models
Defines normalized entities for USERS, PROFILES, SKILLS, USER_SKILLS, CAREER_GOALS, ROADMAPS, ROADMAP_ITEMS, USER_PROGRESS, PROJECT_RECOMMENDATIONS, RESUMES, JOB_DESCRIPTIONS, ASSESSMENTS, and ASSESSMENT_RESULTS.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    """Stores main user profile information and authentication credentials."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(String(100), unique=True, index=True, nullable=True)  # UUID or Supabase/Google Auth ID
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    auth_provider = Column(String(50), default="email")  # "email" or "google"
    is_email_verified = Column(Boolean, default=False)
    
    name = Column(String(100), nullable=False)
    education = Column(String(200), nullable=True)
    experience_level = Column(String(50), default="Beginner")  # Beginner, Intermediate, Advanced
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    progress_entries = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("ProjectRecommendation", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    """Stores extended user onboarding details and career preferences."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    college = Column(String(200), nullable=True)
    degree = Column(String(150), nullable=True)
    department = Column(String(150), nullable=True)
    current_year = Column(String(50), nullable=True)
    graduation_year = Column(String(50), nullable=True)
    secondary_career = Column(String(100), nullable=True)
    preferred_domain = Column(String(100), nullable=True)
    daily_learning_hours = Column(Float, default=2.0)
    learning_preference = Column(String(100), default="Hands-on Projects")
    company_preference = Column(String(100), default="Product Startups")
    location_preference = Column(String(100), default="Remote / Hybrid")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class CareerGoal(Base):
    """Stores user target career path and timeline goals."""
    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(100), nullable=False)
    secondary_role = Column(String(100), nullable=True)
    timeframe_months = Column(Integer, default=6)
    target_salary_tier = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="career_goals")
    roadmaps = relationship("Roadmap", back_populates="career_goal", cascade="all, delete-orphan")


class UserSkill(Base):
    """Stores granular user skills, 6 proficiency levels, confidence scores, and multi-source evidence."""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50), default="INTERMEDIATE")  # NOT_STARTED, BEGINNER, FOUNDATIONAL, INTERMEDIATE, ADVANCED, EXPERT
    confidence_score = Column(Float, default=70.0)  # 0.0 to 100.0%
    status = Column(String(50), default="MASTERED")  # MASTERED, IN_PROGRESS, NEEDS_WORK, MISSING
    evidence_json = Column(Text, nullable=True)  # JSON breakdown of evidence sources

    user = relationship("User", back_populates="skills")


class Roadmap(Base):
    """Stores generated learning roadmap container for a user."""
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_goal_id = Column(Integer, ForeignKey("career_goals.id"), nullable=True)
    total_months = Column(Integer, default=6)
    readiness_score = Column(Float, default=0.0)
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
    phase_name = Column(String(100), default="Core Capability Phase")
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
    verified_by_ai = Column(Boolean, default=False)

    user = relationship("User", back_populates="progress_entries")


class ProjectRecommendation(Base):
    """Stores recommended hands-on portfolio projects matched to user readiness."""
    __tablename__ = "project_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(50), default="BEGINNER")
    match_score = Column(Float, default=85.0)
    required_skills = Column(String(255), nullable=True)
    outcome = Column(Text, nullable=True)
    status = Column(String(50), default="RECOMMENDED")

    user = relationship("User", back_populates="projects")


class Resume(Base):
    """Stores parsed resume details, extracted skills, and keyword gap analysis."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_skills_json = Column(Text, nullable=True)
    score_percentage = Column(Float, default=0.0)
    feedback_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class JobDescription(Base):
    """Stores pasted job descriptions and skill matching analysis."""
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    raw_text = Column(Text, nullable=False)
    extracted_reqs_json = Column(Text, nullable=True)
    match_percentage = Column(Float, default=0.0)
    gap_analysis_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")


class AssessmentResult(Base):
    """Stores quiz/assessment scores and AI interviewer results."""
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_type = Column(String(100), default="Technical")
    skill_name = Column(String(100), nullable=True)
    score_percentage = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessment_results")

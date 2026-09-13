"""
NEXUS AI Agent - Phase 1 Database & Model Tests
Verifies database initialization, user model CRUD operations, relationships, and Pydantic validation schemas.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import User, UserSkill, CareerGoal, Roadmap, UserProgress
from schemas.user import UserCreate, UserProfileResponse

# In-memory SQLite for fast testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Provides a clean in-memory SQLite database session for tests."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_database_tables_creation(db_session):
    """Test that all database tables create without error."""
    user = User(
        name="Pradeesh",
        education="Computer Science Engineering",
        experience_level="Beginner"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.name == "Pradeesh"
    assert user.experience_level == "Beginner"

def test_user_skills_and_career_goal_relationship(db_session):
    """Test adding user skills and career goals via ORM relationships."""
    user = User(
        name="Pradeesh",
        education="Computer Science Engineering",
        experience_level="Beginner"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Add career goal
    goal = CareerGoal(
        user_id=user.id,
        target_role="AI Engineer",
        timeframe_months=6
    )
    db_session.add(goal)

    # Add skills
    skills_data = ["Java", "HTML", "CSS", "JavaScript", "Machine Learning Basics"]
    for s_name in skills_data:
        skill = UserSkill(
            user_id=user.id,
            skill_name=s_name,
            proficiency_level="Beginner",
            status="COMPLETED"
        )
        db_session.add(skill)

    db_session.commit()

    # Query back
    fetched_user = db_session.query(User).filter(User.id == user.id).first()
    assert len(fetched_user.skills) == 5
    assert fetched_user.career_goals[0].target_role == "AI Engineer"

def test_pydantic_schema_validation():
    """Test UserCreate and UserProfileResponse Pydantic schema validation."""
    user_in = UserCreate(
        name="Pradeesh",
        education="Computer Science Engineering",
        experience_level="Beginner",
        career_goal="AI Engineer",
        current_skills=["Java", "HTML", "CSS", "JavaScript", "Machine Learning Basics"]
    )
    assert user_in.name == "Pradeesh"
    assert user_in.career_goal == "AI Engineer"
    assert len(user_in.current_skills) == 5

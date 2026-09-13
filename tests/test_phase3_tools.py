"""
NEXUS AI Agent - Phase 3 Tool Tests
Verifies roadmap generator, project recommender, and progress tracker tools.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import User, UserSkill, CareerGoal, Roadmap, RoadmapItem
from tools.roadmap_generator import generate_roadmap
from tools.project_recommender import recommend_projects
from tools.progress_tracker import update_progress

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Provides an in-memory SQLite DB session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_generate_roadmap_ai_engineer():
    """Test roadmap generator output structure and month items."""
    current_skills = ["Java", "HTML", "CSS", "Machine Learning"]
    target_role = "AI Engineer"

    roadmap_data = generate_roadmap(current_skills, target_role, timeframe_months=6)

    assert roadmap_data["target_role"] == "AI Engineer"
    assert len(roadmap_data["items"]) == 6
    assert "Python" in roadmap_data["summary"]
    assert roadmap_data["items"][0]["month_number"] == 1

def test_recommend_projects():
    """Test project recommender filtering by target role and skill level."""
    target_role = "AI Engineer"
    level = "BEGINNER"

    proj_output = recommend_projects(target_role, level)

    assert proj_output["target_role"] == "AI Engineer"
    assert len(proj_output["recommended_projects"]) > 0
    assert proj_output["recommended_projects"][0]["level"] == "BEGINNER"
    assert "outcome" in proj_output["recommended_projects"][0]

def test_update_progress(db_session):
    """Test progress tracker updating DB records, readiness score, and next recommended topic."""
    # Create user with initial skills
    user = User(name="Pradeesh", education="Computer Science", experience_level="Beginner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    goal = CareerGoal(user_id=user.id, target_role="AI Engineer")
    db_session.add(goal)
    
    initial_skills = ["Java", "HTML", "CSS", "Machine Learning"]
    for s in initial_skills:
        db_session.add(UserSkill(user_id=user.id, skill_name=s, status="COMPLETED"))
    db_session.commit()

    # User completes Python
    progress_result = update_progress(
        user_id=user.id,
        completed_topic="Python",
        db=db_session
    )

    assert progress_result["completed_topic"] == "Python"
    assert progress_result["updated_readiness_score"] > 0.0
    assert progress_result["next_recommended_topic"] is not None
    assert "Python" in progress_result["summary"]

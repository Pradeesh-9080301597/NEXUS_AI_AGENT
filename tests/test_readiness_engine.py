"""
Unit tests for single source of truth readiness engine (tools/readiness_engine.py)
"""

import pytest
from database.database import Base, engine, SessionLocal, init_db
from database.models import User, Profile, CareerGoal, UserSkill, Resume, AssessmentResult, ProjectRecommendation
from tools.readiness_engine import calculate_readiness_score

@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_calculate_readiness_score_new_user(db_session):
    test_user = User(
        email="readiness_test@nexus.ai",
        name="Readiness Tester",
        experience_level="Intermediate"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Goal
    goal = CareerGoal(user_id=test_user.id, target_role="AI Engineer")
    db_session.add(goal)

    # Skills
    s1 = UserSkill(user_id=test_user.id, skill_name="Python", proficiency_level="ADVANCED", confidence_score=85.0)
    s2 = UserSkill(user_id=test_user.id, skill_name="PyTorch", proficiency_level="INTERMEDIATE", confidence_score=70.0)
    db_session.add_all([s1, s2])
    db_session.commit()

    result = calculate_readiness_score(db_session, test_user.id, "AI Engineer")

    assert "overall_score" in result
    assert result["overall_score"] > 0.0
    assert result["target_role"] == "AI Engineer"
    assert "breakdown" in result
    assert "technical_coverage" in result["breakdown"]
    assert "ai_tooling" in result["breakdown"]
    assert "tier" in result

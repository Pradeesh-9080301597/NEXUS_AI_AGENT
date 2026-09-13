"""
NEXUS AI Agent - Phase 4 Agent & Orchestrator Tests
Verifies Orchestrator Agent workflow, intent analysis, planning, LLM service, and persistent memory integration.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import User, UserSkill, CareerGoal
from agent.orchestrator import orchestrator_agent
from agent.intent_analyzer import intent_analyzer
from agent.planner import planner
from memory.memory_manager import memory_manager
from services.llm_service import llm_service

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Provides clean in-memory SQLite database session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_intent_analyzer():
    """Test intent classification rules."""
    assert intent_analyzer.analyze("What skills am I missing?")["intent"] == "IDENTIFY_GAPS"
    assert intent_analyzer.analyze("Generate my learning roadmap")["intent"] == "GENERATE_ROADMAP"
    assert intent_analyzer.analyze("Recommend portfolio projects")["intent"] == "RECOMMEND_PROJECTS"
    assert intent_analyzer.analyze("I completed Python Basics")["intent"] == "UPDATE_PROGRESS"

def test_planner_tool_selection():
    """Test tool sequence selection from intent."""
    plan_gaps = planner.create_plan("IDENTIFY_GAPS", {})
    assert "identify_skill_gaps" in plan_gaps

    plan_roadmap = planner.create_plan("GENERATE_ROADMAP", {})
    assert "generate_roadmap" in plan_roadmap

def test_orchestrator_agent_flow(db_session):
    """Test complete Orchestrator Agent reasoning workflow and response generation."""
    # Seed User Profile in Database Memory
    user = User(name="Pradeesh", education="Computer Science Engineering", experience_level="Beginner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    goal = CareerGoal(user_id=user.id, target_role="AI Engineer")
    db_session.add(goal)

    skills = ["Java", "HTML", "CSS", "JavaScript", "Machine Learning"]
    for s in skills:
        db_session.add(UserSkill(user_id=user.id, skill_name=s, status="COMPLETED"))
    db_session.commit()

    # Process "What skills am I missing?" request
    response = orchestrator_agent.process_request(
        user_id=user.id,
        user_message="What skills am I missing?",
        db=db_session
    )

    assert response.user_id == user.id
    assert response.intent == "IDENTIFY_GAPS"
    assert "identify_skill_gaps" in response.executed_tools
    assert "Python" in response.response_text or "Missing" in response.response_text

def test_orchestrator_progress_update_flow(db_session):
    """Test Orchestrator Agent handling progress completion request."""
    user = User(name="Pradeesh", education="CS", experience_level="Beginner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    db_session.add(CareerGoal(user_id=user.id, target_role="AI Engineer"))
    db_session.commit()

    response = orchestrator_agent.process_request(
        user_id=user.id,
        user_message="I completed Python",
        db=db_session
    )

    assert response.intent == "UPDATE_PROGRESS"
    assert "update_progress" in response.executed_tools
    assert "Python" in response.response_text

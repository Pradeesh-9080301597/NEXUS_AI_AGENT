"""
NEXUS AI Agent - Phase 5 REST API Tests
Verifies FastAPI endpoints using TestClient for profile, skills, analysis, roadmap, progress, projects, and chat endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def api_client():
    """Provides a TestClient with an isolated in-memory SQLite database session using StaticPool."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_health_check(api_client):
    """Test health check endpoint."""
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_profile_endpoints(api_client):
    """Test POST /profile and GET /profile endpoints."""
    profile_payload = {
        "name": "Pradeesh",
        "education": "Computer Science Engineering",
        "experience_level": "Beginner",
        "career_goal": "AI Engineer",
        "current_skills": ["Java", "HTML", "CSS", "JavaScript", "Machine Learning"]
    }

    # Create profile
    post_res = api_client.post("/profile", json=profile_payload)
    assert post_res.status_code == 200
    res_data = post_res.json()
    assert res_data["success"] is True
    user_id = res_data["data"]["user_id"]

    # Fetch profile
    get_res = api_client.get(f"/profile?user_id={user_id}")
    assert get_res.status_code == 200
    profile_info = get_res.json()["data"]
    assert profile_info["name"] == "Pradeesh"
    assert profile_info["career_goal"] == "AI Engineer"

def test_skills_and_analysis_endpoints(api_client):
    """Test POST /skills, GET /skills, and GET /analysis endpoints."""
    # Create User
    post_res = api_client.post("/profile", json={
        "name": "Pradeesh",
        "education": "CS",
        "experience_level": "Beginner",
        "career_goal": "AI Engineer",
        "current_skills": ["Java", "Machine Learning"]
    })
    user_id = post_res.json()["data"]["user_id"]

    # Add Skill
    skill_res = api_client.post(f"/skills?user_id={user_id}", json={
        "skill_name": "HTML",
        "proficiency_level": "Beginner",
        "status": "COMPLETED"
    })
    assert skill_res.status_code == 200

    # Get Skills
    get_skills = api_client.get(f"/skills?user_id={user_id}")
    assert get_skills.status_code == 200

    # Get Analysis
    analysis_res = api_client.get(f"/analysis?user_id={user_id}")
    assert analysis_res.status_code == 200
    report = analysis_res.json()["data"]["report"]
    assert report["target_role"] == "AI Engineer"
    assert "Python" in report["missing_skills"]

def test_roadmap_progress_and_chat_endpoints(api_client):
    """Test POST /roadmap, GET /roadmap, POST /progress, GET /projects, and POST /chat."""
    post_res = api_client.post("/profile", json={
        "name": "Pradeesh",
        "education": "CS",
        "experience_level": "Beginner",
        "career_goal": "AI Engineer",
        "current_skills": ["Java", "Machine Learning"]
    })
    user_id = post_res.json()["data"]["user_id"]

    # Generate Roadmap
    roadmap_res = api_client.post(f"/roadmap?user_id={user_id}&timeframe_months=6")
    assert roadmap_res.status_code == 200

    # Get Roadmap
    get_rm = api_client.get(f"/roadmap?user_id={user_id}")
    assert get_rm.status_code == 200

    # Record Progress
    prog_res = api_client.post(f"/progress?user_id={user_id}", json={
        "topic_completed": "Python",
        "notes": "Completed Python fundamentals"
    })
    assert prog_res.status_code == 200

    # Get Projects
    proj_res = api_client.get(f"/projects?user_id={user_id}")
    assert proj_res.status_code == 200

    # Chat with Agent
    chat_res = api_client.post("/chat", json={
        "user_id": user_id,
        "message": "What skills am I missing?"
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.json()["data"]
    assert chat_data["intent"] == "IDENTIFY_GAPS"

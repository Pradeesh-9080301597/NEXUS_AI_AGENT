"""
Unit tests for NEXUS AI 2.0 tools: resume_analyzer, jd_analyzer, interview_simulator, daily_mission
"""

import pytest
from database.database import SessionLocal, init_db
from database.models import User
from tools.resume_analyzer import analyze_resume
from tools.jd_analyzer import analyze_job_description
from tools.interview_simulator import get_interview_questions, evaluate_interview_answer
from tools.daily_mission import generate_daily_missions

@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_resume_analyzer(db_session):
    sample_text = """
    John Doe - AI Engineer
    Skills: Python, PyTorch, Docker, LangChain, FastAPI, SQL, Streamlit.
    Experience: Built RAG pipelines and fine-tuned LLMs on AWS.
    """
    res = analyze_resume(sample_text, "AI Engineer")
    assert "score_percentage" in res
    assert res["score_percentage"] > 50.0
    assert "Python" in res["extracted_skills"]
    assert "PyTorch" in res["extracted_skills"]

def test_jd_analyzer(db_session):
    sample_jd = """
    We are looking for an AI Engineer proficient in Python, PyTorch, Docker, and Kubernetes.
    Experience with LangChain and vector databases required.
    """
    user_skills = ["Python", "PyTorch", "Docker"]
    res = analyze_job_description("Senior AI Engineer", sample_jd, user_skills)
    assert "match_percentage" in res
    assert res["match_percentage"] > 0.0
    assert "Kubernetes" in res["missing_skills"]

def test_interview_simulator(db_session):
    questions = get_interview_questions("AI Engineer")
    assert len(questions) > 0
    q = questions[0]["question"]
    
    eval_res = evaluate_interview_answer(
        q,
        "Fine-tuning updates model weights for domain style, while RAG fetches live context from a Vector DB like ChromaDB to eliminate knowledge cutoffs and hallucinations without high compute costs.",
        "AI Engineer"
    )
    assert eval_res["score_percentage"] > 60.0
    assert len(eval_res["matched_concepts"]) > 0

def test_daily_missions():
    missions = generate_daily_missions("AI Engineer", ["Kubernetes"])
    assert len(missions) == 3
    assert missions[0]["skill"] == "Kubernetes"

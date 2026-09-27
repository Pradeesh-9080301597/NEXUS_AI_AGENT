"""
NEXUS AI 2.0 - Centralized Single-Source Career Readiness Engine
Calculates multi-dimensional weighted career readiness score across:
- Technical Skill Coverage (35%)
- AI & LLM Tooling (20%)
- Shipped Portfolio Projects (15%)
- Deployment & System Architecture (10%)
- Resume Alignment Score (10%)
- Interview & Assessment Readiness (10%)
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from utils.helpers import get_career_details, normalize_skill
from utils.logger import logger

PROFICIENCY_WEIGHTS = {
    "EXPERT": 100.0,
    "ADVANCED": 85.0,
    "INTERMEDIATE": 65.0,
    "FOUNDATIONAL": 40.0,
    "BEGINNER": 20.0,
    "NOT_STARTED": 0.0,
    "MASTERED": 90.0,
    "NEEDS_WORK": 35.0,
    "MISSING": 0.0,
}

AI_KEYWORDS = [
    "ai", "ml", "machine learning", "deep learning", "llm", "large language model",
    "prompt engineering", "langchain", "llama", "transformers", "pytorch",
    "tensorflow", "vector db", "chromadb", "faiss", "rag", "agents", "fine-tuning", "openai", "gemini"
]

DEPLOY_KEYWORDS = [
    "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git",
    "deployment", "fastapi", "streamlit", "pytest", "devops", "cloud", "rest api"
]

def calculate_readiness_score(
    db: Session,
    user_id: int,
    target_role: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates single source of truth readiness score for a given user.
    Integrates DB records for User, Profile, UserSkill, Resume, AssessmentResult, and ProjectRecommendation.
    """
    from database.models import User, CareerGoal, UserSkill, ProjectRecommendation, Resume, AssessmentResult, RoadmapItem

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Readiness calculation requested for non-existent user_id={user_id}")
        return _default_readiness_response("AI Engineer")

    # 1. Determine Target Role
    if not target_role:
        goal = db.query(CareerGoal).filter(CareerGoal.user_id == user_id).first()
        target_role = goal.target_role if goal else "AI Engineer"

    career_info = get_career_details(target_role)
    required_skills = career_info.get("required_skills", [])
    
    # User's skills map
    user_skills_list = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    user_skill_map = {normalize_skill(s.skill_name): s for s in user_skills_list}

    # ----------------------------------------------------
    # 2. Score 1: Technical Skill Coverage (Weight: 35%)
    # ----------------------------------------------------
    if required_skills:
        req_scores = []
        missing_skills = []
        for req in required_skills:
            req_norm = normalize_skill(req)
            if req_norm in user_skill_map:
                sk = user_skill_map[req_norm]
                prof_score = PROFICIENCY_WEIGHTS.get(sk.proficiency_level.upper(), 50.0)
                conf_score = sk.confidence_score if sk.confidence_score is not None else prof_score
                req_scores.append((prof_score + conf_score) / 2.0)
            else:
                req_scores.append(0.0)
                missing_skills.append(req)
        s_tech = sum(req_scores) / len(req_scores)
    else:
        s_tech = 50.0
        missing_skills = []

    # ----------------------------------------------------
    # 3. Score 2: AI & LLM Tooling (Weight: 20%)
    # ----------------------------------------------------
    ai_scores = []
    for sk in user_skills_list:
        sk_name_norm = normalize_skill(sk.skill_name)
        if any(kw in sk_name_norm for kw in AI_KEYWORDS):
            prof_score = PROFICIENCY_WEIGHTS.get(sk.proficiency_level.upper(), 50.0)
            ai_scores.append(prof_score)

    if ai_scores:
        s_ai = sum(ai_scores) / len(ai_scores)
    else:
        # Fallback based on tech score & experience level
        exp_baseline = {"Beginner": 30.0, "Intermediate": 55.0, "Advanced": 80.0}.get(user.experience_level, 40.0)
        s_ai = min(s_tech, exp_baseline)

    # ----------------------------------------------------
    # 4. Score 3: Shipped Portfolio Projects (Weight: 15%)
    # ----------------------------------------------------
    user_projects = db.query(ProjectRecommendation).filter(ProjectRecommendation.user_id == user_id).all()
    if user_projects:
        proj_scores = []
        for p in user_projects:
            st = (p.status or "").upper()
            if st == "COMPLETED":
                proj_scores.append(100.0)
            elif st == "IN_PROGRESS":
                proj_scores.append(50.0)
            elif st == "SUBMITTED":
                proj_scores.append(85.0)
            else:
                proj_scores.append(20.0)
        s_projects = sum(proj_scores) / len(proj_scores)
    else:
        s_projects = 25.0  # Initial baseline before adding projects

    # ----------------------------------------------------
    # 5. Score 4: System Architecture & Deployment (Weight: 10%)
    # ----------------------------------------------------
    deploy_scores = []
    for sk in user_skills_list:
        sk_name_norm = normalize_skill(sk.skill_name)
        if any(kw in sk_name_norm for kw in DEPLOY_KEYWORDS):
            prof_score = PROFICIENCY_WEIGHTS.get(sk.proficiency_level.upper(), 50.0)
            deploy_scores.append(prof_score)

    if deploy_scores:
        s_deploy = sum(deploy_scores) / len(deploy_scores)
    else:
        s_deploy = 30.0  # Default baseline

    # ----------------------------------------------------
    # 6. Score 5: Resume Alignment Score (Weight: 10%)
    # ----------------------------------------------------
    latest_resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
    if latest_resume and latest_resume.score_percentage > 0:
        s_resume = latest_resume.score_percentage
    else:
        # Fallback profile completeness
        s_resume = 45.0 if user.profile else 30.0

    # ----------------------------------------------------
    # 7. Score 6: Interview & Assessment Readiness (Weight: 10%)
    # ----------------------------------------------------
    assessments = db.query(AssessmentResult).filter(AssessmentResult.user_id == user_id).all()
    if assessments:
        s_prep = sum(a.score_percentage for a in assessments) / len(assessments)
    else:
        # Fallback based on completed roadmap items
        roadmap_items = db.query(RoadmapItem).join(RoadmapItem.roadmap).filter(RoadmapItem.roadmap.has(user_id=user_id)).all()
        if roadmap_items:
            completed_count = sum(1 for item in roadmap_items if item.status == "COMPLETED")
            s_prep = (completed_count / len(roadmap_items)) * 100.0
        else:
            s_prep = 20.0

    # ----------------------------------------------------
    # 8. Compute Weighted Total Score
    # ----------------------------------------------------
    total_score = (
        0.35 * s_tech +
        0.20 * s_ai +
        0.15 * s_projects +
        0.10 * s_deploy +
        0.10 * s_resume +
        0.10 * s_prep
    )
    total_score = round(min(max(total_score, 0.0), 100.0), 1)

    # Tier Classification
    if total_score >= 85.0:
        tier = "JOB_READY"
        tier_label = "Production Ready & Job Fit"
    elif total_score >= 70.0:
        tier = "ADVANCED_CANDIDATE"
        tier_label = "Advanced Candidate"
    elif total_score >= 50.0:
        tier = "INTERMEDIATE_BUILDER"
        tier_label = "Intermediate Builder"
    else:
        tier = "EARLY_LEARNER"
        tier_label = "Foundational Learner"

    # Actionable Recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(f"Master core missing skills for {target_role}: {', '.join(missing_skills[:3])}")
    if s_projects < 60.0:
        recommendations.append("Build and ship at least 1 end-to-end portfolio project to boost practical score.")
    if s_deploy < 50.0:
        recommendations.append("Learn containerization (Docker) and REST API deployment to improve system architecture score.")
    if s_resume < 50.0:
        recommendations.append("Upload your latest resume to analyze ATS keyword match score.")
    if not recommendations:
        recommendations.append("Maintain current momentum by completing mock technical interviews!")

    return {
        "overall_score": total_score,
        "target_role": target_role,
        "tier": tier,
        "tier_label": tier_label,
        "breakdown": {
            "technical_coverage": round(s_tech, 1),
            "ai_tooling": round(s_ai, 1),
            "projects_shipped": round(s_projects, 1),
            "deployment_arch": round(s_deploy, 1),
            "resume_alignment": round(s_resume, 1),
            "interview_prep": round(s_prep, 1),
        },
        "top_gaps": missing_skills[:5],
        "recommendations": recommendations
    }

def _default_readiness_response(target_role: str) -> Dict[str, Any]:
    """Default fallback dictionary when user data is empty."""
    return {
        "overall_score": 0.0,
        "target_role": target_role,
        "tier": "EARLY_LEARNER",
        "tier_label": "Foundational Learner",
        "breakdown": {
            "technical_coverage": 0.0,
            "ai_tooling": 0.0,
            "projects_shipped": 0.0,
            "deployment_arch": 0.0,
            "resume_alignment": 0.0,
            "interview_prep": 0.0,
        },
        "top_gaps": [],
        "recommendations": ["Complete profile onboarding to initialize your career readiness index."]
    }

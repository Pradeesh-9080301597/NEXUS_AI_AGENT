"""
NEXUS AI Agent - FastAPI REST API Application
Provides RESTful endpoints for user profiles, skill analysis, roadmaps, progress tracking, project recommendations, and AI agent chat.
"""

from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database.database import get_db, init_db
from database.models import User, UserSkill, CareerGoal, Roadmap, RoadmapItem, UserProgress
from schemas.user import UserCreate, UserProfileResponse, SkillCreate, SkillResponse
from schemas.roadmap import SkillGapReport, RoadmapResponse, ProgressUpdateCreate, ProgressUpdateResponse, ProjectRecommendationResponse
from schemas.response import APIResponse, ChatRequest, AgentResponse
from tools.skill_analyzer import analyze_skills
from tools.skill_gap_analyzer import identify_skill_gaps
from tools.roadmap_generator import generate_roadmap
from tools.project_recommender import recommend_projects
from tools.progress_tracker import update_progress
from agent.orchestrator import orchestrator_agent
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events handler."""
    logger.info("Starting NEXUS REST API Server...")
    init_db()
    yield
    logger.info("Shutting down NEXUS REST API Server...")

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API Ecosystem for NEXUS Autonomous AI Career Intelligence Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
def health_check():
    """Health check endpoint confirming API status."""
    return {"status": "online", "app": settings.APP_NAME}


# --- USER PROFILE ENDPOINTS ---

@app.post("/profile", response_model=APIResponse, tags=["Profile"])
def create_or_update_profile(user_in: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user profile with initial skills and career goal."""
    try:
        # Create user record
        user = User(
            name=user_in.name,
            education=user_in.education,
            experience_level=user_in.experience_level
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create career goal
        goal = CareerGoal(
            user_id=user.id,
            target_role=user_in.career_goal,
            timeframe_months=6
        )
        db.add(goal)

        # Add initial skills
        for skill_name in user_in.current_skills:
            s_obj = UserSkill(
                user_id=user.id,
                skill_name=skill_name.strip(),
                proficiency_level=user_in.experience_level,
                status="COMPLETED"
            )
            db.add(s_obj)

        db.commit()
        db.refresh(user)

        logger.info(f"Created profile for '{user.name}' (user_id={user.id})")

        return APIResponse(
            success=True,
            message="User profile created successfully.",
            data={"user_id": user.id, "name": user.name, "career_goal": user_in.career_goal}
        )
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile", response_model=APIResponse, tags=["Profile"])
def get_profile(user_id: int = Query(..., description="Target user ID"), db: Session = Depends(get_db)):
    """Retrieves complete profile details for a given user ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

    target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
    skills_data = [SkillResponse.model_validate(s) for s in user.skills]

    profile_data = {
        "user_id": user.id,
        "name": user.name,
        "education": user.education,
        "experience_level": user.experience_level,
        "career_goal": target_role,
        "skills": skills_data,
        "created_at": user.created_at
    }

    return APIResponse(success=True, message="Profile retrieved successfully.", data=profile_data)


# --- SKILL ENDPOINTS ---

@app.post("/skills", response_model=APIResponse, tags=["Skills"])
def add_user_skill(user_id: int, skill_in: SkillCreate, db: Session = Depends(get_db)):
    """Adds or updates a skill in the user's inventory."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    skill_obj = UserSkill(
        user_id=user_id,
        skill_name=skill_in.skill_name,
        proficiency_level=skill_in.proficiency_level,
        status=skill_in.status
    )
    db.add(skill_obj)
    db.commit()

    return APIResponse(success=True, message=f"Added skill '{skill_in.skill_name}'.", data={"user_id": user_id})


@app.get("/skills", response_model=APIResponse, tags=["Skills"])
def get_user_skills(user_id: int, db: Session = Depends(get_db)):
    """Lists all skills for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    skills = [SkillResponse.model_validate(s) for s in user.skills]
    return APIResponse(success=True, message="Skills retrieved.", data=skills)


# --- ANALYSIS ENDPOINTS ---

@app.get("/analysis", response_model=APIResponse, tags=["Skill Analysis"])
def get_skill_analysis(user_id: int, db: Session = Depends(get_db)):
    """Generates skill gap report comparing user skills against career goals."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
    current_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]

    analysis_data = identify_skill_gaps(current_skills, target_role)
    return APIResponse(success=True, message="Skill gap analysis complete.", data=analysis_data)


# --- ROADMAP ENDPOINTS ---

@app.post("/roadmap", response_model=APIResponse, tags=["Roadmap"])
def generate_user_roadmap(user_id: int, timeframe_months: int = 6, db: Session = Depends(get_db)):
    """Generates and stores a new learning roadmap for the user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
    current_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]

    roadmap_data = generate_roadmap(
        current_skills=current_skills,
        target_role=target_role,
        experience_level=user.experience_level,
        timeframe_months=timeframe_months
    )

    # Persist in DB
    goal_id = user.career_goals[0].id if user.career_goals else None
    roadmap_obj = Roadmap(
        user_id=user_id,
        career_goal_id=goal_id,
        total_months=timeframe_months
    )
    db.add(roadmap_obj)
    db.commit()
    db.refresh(roadmap_obj)

    for item in roadmap_data["items"]:
        item_obj = RoadmapItem(
            roadmap_id=roadmap_obj.id,
            month_number=item["month_number"],
            topic_name=item["topic_name"],
            objectives=item["objectives"],
            duration=item["duration"],
            practice_tasks=item["practice_tasks"],
            status=item["status"]
        )
        db.add(item_obj)

    db.commit()

    return APIResponse(success=True, message="Roadmap generated & saved.", data=roadmap_data)


@app.get("/roadmap", response_model=APIResponse, tags=["Roadmap"])
def get_user_roadmap(user_id: int, db: Session = Depends(get_db)):
    """Fetches current stored roadmap for a user."""
    roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.id.desc()).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found for user.")

    items = [
        {
            "month_number": item.month_number,
            "topic_name": item.topic_name,
            "objectives": item.objectives,
            "duration": item.duration,
            "practice_tasks": item.practice_tasks,
            "status": item.status
        }
        for item in roadmap.items
    ]

    return APIResponse(
        success=True,
        message="Roadmap retrieved.",
        data={"roadmap_id": roadmap.id, "total_months": roadmap.total_months, "items": items}
    )


# --- PROGRESS ENDPOINTS ---

@app.post("/progress", response_model=APIResponse, tags=["Progress"])
def record_progress(user_id: int, progress_in: ProgressUpdateCreate, db: Session = Depends(get_db)):
    """Submits completed learning topic and updates readiness score."""
    try:
        res = update_progress(user_id=user_id, completed_topic=progress_in.topic_completed, db=db, notes=progress_in.notes)
        return APIResponse(success=True, message="Progress recorded.", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


# --- PROJECT ENDPOINTS ---

@app.get("/projects", response_model=APIResponse, tags=["Projects"])
def get_project_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Recommends portfolio projects suited for the user's skill level."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
    projects = recommend_projects(target_role=target_role, experience_level=user.experience_level)
    return APIResponse(success=True, message="Project recommendations retrieved.", data=projects)


# --- CHAT / AI AGENT ENDPOINT ---

@app.post("/chat", response_model=APIResponse, tags=["AI Agent"])
def chat_with_agent(chat_in: ChatRequest, db: Session = Depends(get_db)):
    """Primary chat endpoint interacting with NEXUS Autonomous AI Career Agent."""
    try:
        agent_res = orchestrator_agent.process_request(
            user_id=chat_in.user_id,
            user_message=chat_in.message,
            db=db
        )
        return APIResponse(success=True, message="Agent response generated.", data=agent_res.model_dump())
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

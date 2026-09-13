"""
NEXUS AI Agent - Roadmap & Analysis Pydantic Schemas
Defines request and response schemas for skill analysis, roadmaps, progress, and project recommendations.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SkillItemStatus(BaseModel):
    skill_name: str
    status: str  # COMPLETED, IN_PROGRESS, MISSING, OPTIONAL
    importance_reason: str

class SkillGapReport(BaseModel):
    target_role: str
    total_required_skills: int
    completed_skills: List[str]
    in_progress_skills: List[str]
    missing_skills: List[str]
    optional_skills: List[str]
    readiness_score_percentage: float
    skill_details: List[SkillItemStatus]

class RoadmapItemBase(BaseModel):
    month_number: int
    topic_name: str
    objectives: str
    duration: str = "4 Weeks"
    practice_tasks: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED

class RoadmapItemResponse(RoadmapItemBase):
    id: int
    roadmap_id: int

    model_config = ConfigDict(from_attributes=True)

class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    career_goal_id: Optional[int]
    total_months: int
    items: List[RoadmapItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProgressUpdateCreate(BaseModel):
    topic_completed: str = Field(..., description="Topic or module completed by user")
    notes: Optional[str] = Field(None, description="Optional notes or feedback")

class ProgressUpdateResponse(BaseModel):
    id: int
    user_id: int
    topic_completed: str
    completed_at: datetime
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ProjectRecommendationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    level: str  # BEGINNER, INTERMEDIATE, ADVANCED
    required_skills: str
    status: str

    model_config = ConfigDict(from_attributes=True)

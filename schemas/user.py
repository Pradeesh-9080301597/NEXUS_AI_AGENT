"""
NEXUS AI Agent - User Pydantic Schemas
Defines request and response schemas for authentication, profile, skills, and career goals.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

# --- AUTHENTICATION SCHEMAS ---

class UserRegister(BaseModel):
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password (min 6 characters)")

class UserLogin(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

class GoogleAuthInput(BaseModel):
    email: str
    name: Optional[str] = None
    google_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class AuthTokenResponse(BaseModel):
    user_id: int
    email: str
    name: str
    access_token: str
    token_type: str = "bearer"

# --- PROFILE & SKILL SCHEMAS ---

class SkillBase(BaseModel):
    skill_name: str = Field(..., description="Name of the skill, e.g. Python, Java")
    proficiency_level: str = Field("Beginner", description="Proficiency level: Beginner, Intermediate, Advanced")
    status: str = Field("COMPLETED", description="Skill status: COMPLETED, IN_PROGRESS, MISSING, OPTIONAL")

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class CareerGoalBase(BaseModel):
    target_role: str = Field(..., description="Target career role, e.g. AI Engineer")
    timeframe_months: int = Field(6, description="Timeline in months")
    target_salary_tier: Optional[str] = None

class CareerGoalCreate(CareerGoalBase):
    pass

class CareerGoalResponse(CareerGoalBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    name: str = Field(..., description="User full name")
    email: Optional[str] = Field(None, description="User email address")
    education: Optional[str] = Field(None, description="Degree or educational background")
    experience_level: str = Field("Beginner", description="Experience level: Beginner, Intermediate, Advanced")
    career_goal: str = Field(..., description="Primary target career role")
    current_skills: List[str] = Field(default_factory=list, description="List of current skills")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    experience_level: Optional[str] = None
    career_goal: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: str
    education: Optional[str]
    experience_level: str
    career_goal: Optional[str]
    skills: List[SkillResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

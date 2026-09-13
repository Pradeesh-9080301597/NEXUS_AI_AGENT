"""
NEXUS AI Agent - Memory Manager Module
Handles persistent SQLite database memory load/store operations for user profile, skills, roadmaps, and progress.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from database.models import User, UserSkill, CareerGoal, UserProgress, Roadmap
from utils.logger import logger

class MemoryManager:
    """Manages short-term conversation context and persistent relational memory."""

    @staticmethod
    def get_user_memory(user_id: int, db: Session) -> Dict[str, Any]:
        """Loads complete user context from persistent SQLite database."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with id {user_id} not found in memory.")
            return {
                "user_id": user_id,
                "name": "Guest User",
                "education": "Not Specified",
                "experience_level": "Beginner",
                "career_goal": "AI Engineer",
                "current_skills": [],
                "completed_topics": [],
                "has_profile": False
            }

        target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
        completed_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]
        in_progress_skills = [s.skill_name for s in user.skills if s.status == "IN_PROGRESS"]
        completed_topics = [p.topic_completed for p in user.progress_entries]

        return {
            "user_id": user.id,
            "name": user.name,
            "education": user.education,
            "experience_level": user.experience_level,
            "career_goal": target_role,
            "current_skills": completed_skills,
            "in_progress_skills": in_progress_skills,
            "completed_topics": completed_topics,
            "has_profile": True,
            "created_at": user.created_at
        }

    @staticmethod
    def format_memory_summary(memory: Dict[str, Any]) -> str:
        """Formats user profile memory into a concise text block for agent prompt context."""
        skills_str = ", ".join(memory["current_skills"]) if memory["current_skills"] else "None recorded"
        topics_str = ", ".join(memory["completed_topics"]) if memory["completed_topics"] else "None recorded"

        return (
            f"👤 **User Profile**: {memory['name']} | Education: {memory['education']} | Level: {memory['experience_level']}\n"
            f"🎯 **Target Career Goal**: {memory['career_goal']}\n"
            f"⚡ **Current Mastered Skills**: {skills_str}\n"
            f"📌 **Completed Progress Topics**: {topics_str}"
        )

memory_manager = MemoryManager()

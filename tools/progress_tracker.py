"""
NEXUS AI Agent - Progress Tracker Tool
Updates user progress when learning topics or skills are completed.
Recalculates career readiness, updates roadmap item status, and identifies the next recommended topic.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import User, UserSkill, UserProgress, Roadmap, RoadmapItem
from tools.skill_analyzer import analyze_skills
from utils.logger import logger

def update_progress(
    user_id: int,
    completed_topic: str,
    db: Session,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates progress record for a user upon topic completion.
    
    Actions:
    1. Records completion in UserProgress.
    2. Updates or adds matching skill in UserSkill with COMPLETED status.
    3. Marks corresponding RoadmapItem as COMPLETED.
    4. Calculates updated readiness score and next recommended topic.
    """
    logger.info(f"Updating progress for user_id={user_id}: Completed topic '{completed_topic}'")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} not found.")

    # 1. Store UserProgress entry
    progress_entry = UserProgress(
        user_id=user_id,
        topic_completed=completed_topic,
        notes=notes or f"Completed {completed_topic}"
    )
    db.add(progress_entry)

    # 2. Update UserSkill list
    existing_skills = {s.skill_name.lower(): s for s in user.skills}
    topic_clean = completed_topic.strip()

    if topic_clean.lower() in existing_skills:
        skill_obj = existing_skills[topic_clean.lower()]
        skill_obj.status = "COMPLETED"
    else:
        new_skill = UserSkill(
            user_id=user_id,
            skill_name=topic_clean,
            proficiency_level="Intermediate",
            status="COMPLETED"
        )
        db.add(new_skill)

    # 3. Update RoadmapItem if user has an active roadmap
    roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.id.desc()).first()
    if roadmap:
        for item in roadmap.items:
            if topic_clean.lower() in item.topic_name.lower() or item.topic_name.lower() in topic_clean.lower():
                item.status = "COMPLETED"

    db.commit()
    db.refresh(user)

    # Re-fetch updated user skills & target role
    updated_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]
    target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"

    # 4. Perform re-analysis
    analysis = analyze_skills(updated_skills, target_role)
    missing_skills = analysis.get("missing_skills", [])
    next_topic = missing_skills[0] if missing_skills else "All core skills completed! Advanced projects recommended."

    result = {
        "user_id": user_id,
        "completed_topic": completed_topic,
        "updated_readiness_score": analysis["readiness_score_percentage"],
        "next_recommended_topic": next_topic,
        "remaining_missing_skills": missing_skills,
        "total_completed_skills_count": len(updated_skills)
    }

    result["summary"] = (
        f"🎉 **Progress Updated!**\n"
        f"✅ Marked **'{completed_topic}'** as Completed.\n"
        f"📈 **Updated Readiness Score**: {result['updated_readiness_score']}%\n"
        f"➡️ **Next Recommended Topic to Learn**: **{next_topic}**"
    )

    logger.info(f"Progress update successful for user_id={user_id}. Next topic: {next_topic}")
    return result

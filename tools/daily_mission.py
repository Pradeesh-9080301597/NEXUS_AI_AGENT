"""
NEXUS AI 2.0 - Daily Career Missions Engine Tool
Generates daily micro-missions and actionable skill challenges for users based on readiness gaps.
"""

from typing import Dict, Any, List
from utils.logger import logger

MISSION_TEMPLATES = {
    "AI Engineer": [
        {
            "id": "m1",
            "title": "Build a RAG Pipeline with ChromaDB",
            "category": "Practical Project",
            "estimated_minutes": 45,
            "reward_points": 150,
            "skill": "RAG / Vector DB",
            "task_description": "Implement a local Python script using ChromaDB and LangChain to index 3 PDF papers and query them with semantic search."
        },
        {
            "id": "m2",
            "title": "Containerize a FastAPI Backend",
            "category": "Deployment",
            "estimated_minutes": 30,
            "reward_points": 100,
            "skill": "Docker",
            "task_description": "Write a multi-stage `Dockerfile` for a FastAPI app, build the image, and test running it locally on port 8000."
        },
        {
            "id": "m3",
            "title": "Mock Technical Interview Practice",
            "category": "Assessment",
            "estimated_minutes": 20,
            "reward_points": 80,
            "skill": "Interview Prep",
            "task_description": "Complete 1 practice technical interview question in the AI Interviewer tab and review the model answer."
        }
    ],
    "Data Scientist": [
        {
            "id": "m1",
            "title": "Exploratory Data Analysis on Imbalanced Dataset",
            "category": "Data Science",
            "estimated_minutes": 40,
            "reward_points": 120,
            "skill": "Pandas / Seaborn",
            "task_description": "Plot feature distributions and compute correlation matrices for a credit risk dataset."
        }
    ]
}

def generate_daily_missions(target_role: str = "AI Engineer", top_gaps: List[str] = None) -> List[Dict[str, Any]]:
    """Generates personalized daily career missions."""
    logger.info(f"Generating daily missions for {target_role} with gaps: {top_gaps}")
    
    base_missions = MISSION_TEMPLATES.get(target_role, MISSION_TEMPLATES["AI Engineer"])
    
    # If user has specific gaps, inject a custom gap mission
    if top_gaps:
        gap_skill = top_gaps[0]
        gap_mission = {
            "id": "m_gap_1",
            "title": f"Master Foundations of {gap_skill}",
            "category": "Targeted Skill Gap",
            "estimated_minutes": 35,
            "reward_points": 120,
            "skill": gap_skill,
            "task_description": f"Read documentation or complete 1 practice script implementing core concepts of {gap_skill}."
        }
        return [gap_mission] + base_missions[:2]
    
    return base_missions

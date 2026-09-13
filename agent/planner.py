"""
NEXUS AI Agent - Planner Module
Translates user intent and context into an actionable tool execution plan.
"""

from typing import Dict, Any, List
from utils.logger import logger

class AgentPlanner:
    """Formulates sequential tool call execution plans."""

    @staticmethod
    def create_plan(intent: str, user_context: Dict[str, Any]) -> List[str]:
        """Determines required tool sequence based on intent and user memory."""
        logger.info(f"Planning execution for intent '{intent}'")

        if intent == "ANALYZE_SKILLS":
            return ["analyze_skills"]
        elif intent == "IDENTIFY_GAPS":
            return ["identify_skill_gaps"]
        elif intent == "GENERATE_ROADMAP":
            return ["identify_skill_gaps", "generate_roadmap"]
        elif intent == "RECOMMEND_PROJECTS":
            return ["recommend_projects"]
        elif intent == "UPDATE_PROGRESS":
            return ["update_progress"]
        elif intent == "GET_PROFILE":
            return ["get_user_profile"]
        else:
            # Fallback strategy: evaluate skill gap & generate roadmap guidance
            return ["identify_skill_gaps"]

planner = AgentPlanner()

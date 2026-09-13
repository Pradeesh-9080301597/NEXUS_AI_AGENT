"""
NEXUS AI Agent - Orchestrator Agent Engine
Main cognitive agent engine coordinating intent analysis, memory lookup, tool execution, and response synthesis.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agent.intent_analyzer import intent_analyzer
from agent.planner import planner
from agent.evaluator import evaluator
from memory.memory_manager import memory_manager
from tools.skill_analyzer import analyze_skills
from tools.skill_gap_analyzer import identify_skill_gaps
from tools.roadmap_generator import generate_roadmap
from tools.project_recommender import recommend_projects
from tools.progress_tracker import update_progress
from utils.logger import logger
from schemas.response import AgentResponse

class OrchestratorAgent:
    """Autonomous AI Career Agent implementing the multi-step reasoning workflow."""

    def process_request(
        self,
        user_id: int,
        user_message: str,
        db: Session
    ) -> AgentResponse:
        """
        Executes the full reasoning loop:
        OBSERVE -> INTENT -> CHECK PROFILE -> PLAN -> SELECT TOOLS -> EXECUTE -> EVALUATE -> RESPOND -> UPDATE MEMORY
        """
        logger.info(f"--- [ORCHESTRATOR START] User ID: {user_id} | Message: '{user_message}' ---")

        # 1. OBSERVE & CHECK USER PROFILE (Memory Lookup)
        user_memory = memory_manager.get_user_memory(user_id, db)

        # 2. UNDERSTAND USER INTENT
        intent_info = intent_analyzer.analyze(user_message)
        intent = intent_info["intent"]

        # 3. DECIDE REQUIRED ACTION & PLAN TOOL SELECTION
        tool_sequence = planner.create_plan(intent, user_memory)

        # 4. EXECUTE SELECTED TOOLS
        executed_tools = []
        tool_results: Dict[str, Any] = {}

        current_skills = user_memory.get("current_skills", ["Python", "Git"])
        target_role = user_memory.get("career_goal", "AI Engineer")
        exp_level = user_memory.get("experience_level", "Beginner")

        for tool_name in tool_sequence:
            logger.info(f"Executing selected tool: '{tool_name}'")
            executed_tools.append(tool_name)

            if tool_name == "analyze_skills":
                tool_results[tool_name] = analyze_skills(current_skills, target_role)

            elif tool_name == "identify_skill_gaps":
                tool_results[tool_name] = identify_skill_gaps(current_skills, target_role)

            elif tool_name == "generate_roadmap":
                tool_results[tool_name] = generate_roadmap(
                    current_skills=current_skills,
                    target_role=target_role,
                    experience_level=exp_level
                )

            elif tool_name == "recommend_projects":
                tool_results[tool_name] = recommend_projects(
                    target_role=target_role,
                    experience_level=exp_level
                )

            elif tool_name == "update_progress":
                # Extract topic completed from message
                topic_extracted = intent_info.get("extracted_topic", user_message)
                # Clean up query prefixes if present
                for prefix in ["i completed ", "i learned ", "completed ", "finished "]:
                    if topic_extracted.lower().startswith(prefix):
                        topic_extracted = topic_extracted[len(prefix):]
                
                tool_results[tool_name] = update_progress(
                    user_id=user_id,
                    completed_topic=topic_extracted,
                    db=db
                )

            elif tool_name == "get_user_profile":
                tool_results[tool_name] = {
                    "summary": memory_manager.format_memory_summary(user_memory),
                    "memory": user_memory
                }

        # 5. VALIDATE RESULT & GENERATE RESPONSE
        response_text = evaluator.evaluate_and_respond(
            user_message=user_message,
            intent=intent,
            tool_results=tool_results,
            user_memory=user_memory
        )

        logger.info(f"--- [ORCHESTRATOR COMPLETE] Intent: {intent} | Executed: {executed_tools} ---")

        return AgentResponse(
            user_id=user_id,
            intent=intent,
            action_taken=f"Executed tools: {', '.join(executed_tools)}",
            executed_tools=executed_tools,
            response_text=response_text,
            data=tool_results
        )

orchestrator_agent = OrchestratorAgent()

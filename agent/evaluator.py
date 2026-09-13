"""
NEXUS AI Agent - Evaluator Module
Validates tool execution results and synthesizes clear, structured response text.
"""

from typing import Dict, Any, List
from services.llm_service import llm_service
from prompts.system_prompt import NEXUS_SYSTEM_PROMPT
from utils.logger import logger

class AgentEvaluator:
    """Validates tool execution results and produces final synthesized response."""

    @staticmethod
    def evaluate_and_respond(
        user_message: str,
        intent: str,
        tool_results: Dict[str, Any],
        user_memory: Dict[str, Any]
    ) -> str:
        """Synthesizes structured tool output into clear, friendly guidance."""
        logger.info(f"Evaluating tool execution results for intent: '{intent}'")

        # Extract textual summary from tool results if available
        summaries = []
        for tool_name, data in tool_results.items():
            if isinstance(data, dict) and "summary" in data:
                summaries.append(data["summary"])

        if summaries:
            base_output = "\n\n---\n\n".join(summaries)
        else:
            base_output = f"Processed request for {user_memory.get('name', 'User')}."

        # Prompt LLM to enrich output if available
        enrichment_prompt = (
            f"User Profile: {user_memory}\n"
            f"Executed Tool Results:\n{base_output}\n\n"
            f"User Prompt: {user_message}\n\n"
            f"Synthesize a clear, encouraging, structured response as NEXUS AI Career Coach."
        )

        final_response = llm_service.generate_response(NEXUS_SYSTEM_PROMPT, enrichment_prompt)

        # If LLM returned generic fallback, use direct clean tool summary
        if "I have processed your request" in final_response or not final_response:
            return base_output

        return final_response

evaluator = AgentEvaluator()

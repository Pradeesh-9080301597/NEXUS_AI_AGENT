"""
NEXUS AI Agent - LLM Service Module
Provides unified interface to Gemini / LLM API with intelligent fallback execution when API keys are unconfigured.
"""

import json
from typing import Dict, Any, Optional
from config import settings
from utils.logger import logger

class LLMService:
    """Manages LLM API calls, prompt construction, and response parsing."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.LLM_MODEL_NAME
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initializes Google GenAI client if API key is configured."""
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"LLM Client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize GenAI client: {e}. Falling back to rule-based engine.")
                self.client = None
        else:
            logger.info("No LLM API Key provided in .env. Running in offline/rule-based mode.")

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generates conversational text response using LLM or rule-based fallback."""
        if self.client:
            try:
                prompt_text = f"{system_prompt}\n\nUser Request: {user_prompt}"
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_text
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Error calling LLM API: {e}")

        # Fallback response if API call fails or key is unconfigured
        return self._generate_rule_based_fallback(user_prompt)

    def extract_intent(self, user_message: str) -> Dict[str, Any]:
        """Classifies user intent using LLM or pattern matching."""
        msg_lower = user_message.lower()

        if "missing" in msg_lower or "gap" in msg_lower:
            intent = "IDENTIFY_GAPS"
        elif "roadmap" in msg_lower or "plan" in msg_lower or "curriculum" in msg_lower:
            intent = "GENERATE_ROADMAP"
        elif "project" in msg_lower or "build" in msg_lower or "portfolio" in msg_lower:
            intent = "RECOMMEND_PROJECTS"
        elif "completed" in msg_lower or "finished" in msg_lower or "learned" in msg_lower:
            intent = "UPDATE_PROGRESS"
        elif "skill" in msg_lower or "know" in msg_lower or "analyze" in msg_lower:
            intent = "ANALYZE_SKILLS"
        elif "profile" in msg_lower or "who am i" in msg_lower or "my goal" in msg_lower:
            intent = "GET_PROFILE"
        else:
            intent = "GENERAL_CAREER_ADVICE"

        return {
            "intent": intent,
            "extracted_topic": user_message,
            "reasoning": f"Pattern matched intent '{intent}' based on query terms."
        }

    def _generate_rule_based_fallback(self, user_prompt: str) -> str:
        """Provides structured guidance when LLM API is unavailable."""
        return (
            f"🤖 **NEXUS Career Assistant Guidance**\n\n"
            f"I have processed your request: *\"{user_prompt}\"*\n\n"
            f"Based on your profile, I recommend focusing on building foundational skills, "
            f"completing hands-on projects, and updating your progress regularly to increase your readiness score."
        )

llm_service = LLMService()

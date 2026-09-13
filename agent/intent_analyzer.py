"""
NEXUS AI Agent - Intent Analyzer Module
Understands user requests and categorizes them into actionable agent intents.
"""

from typing import Dict, Any
from services.llm_service import llm_service
from utils.logger import logger

class IntentAnalyzer:
    """Analyzes user message intent using LLM or rule-based pattern matching."""

    @staticmethod
    def analyze(user_message: str) -> Dict[str, Any]:
        """Classifies intent and extracts relevant key concepts."""
        logger.info(f"Analyzing intent for user input: '{user_message}'")
        analysis = llm_service.extract_intent(user_message)
        logger.info(f"Identified intent: {analysis['intent']}")
        return analysis

intent_analyzer = IntentAnalyzer()

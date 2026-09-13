"""
NEXUS AI Agent - Standard Response Schemas
Defines API response wrappers, agent output schemas, and chat models.
"""

from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    """Standard unified REST API response wrapper."""
    success: bool = True
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(..., description="User message or career query")

class AgentResponse(BaseModel):
    user_id: int
    intent: str
    action_taken: str
    executed_tools: List[str] = []
    response_text: str
    data: Optional[Dict[str, Any]] = None

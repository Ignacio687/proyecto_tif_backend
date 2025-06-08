from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class Conversation(BaseModel):
    user_input: str = Field(..., description="User input for the assistant")
    server_reply: str = Field(..., description="Server's reply to the user")
    timestamp: datetime = Field(default_factory=utc_now, description="Timestamp of the interaction")

class Skill(BaseModel):
    name: str
    action: str
    params: Dict[str, Any]

class ServerResponse(BaseModel):
    server_reply: str
    app_params: Optional[List[Dict[str, bool]]] = None
    skills: Optional[List[Skill]] = None

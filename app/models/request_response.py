from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Conversation(BaseModel):
    user_input: str = Field(..., description="User input for the assistant")
    server_reply: str = Field(..., description="Server's reply to the user")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the interaction")

class UserRequest(BaseModel):
    user_req: str = Field(..., description="User input for the assistant")

class Skill(BaseModel):
    name: str
    action: str
    params: Dict[str, Any]

class ServerResponse(BaseModel):
    server_reply: str
    app_params: Optional[List[Any]] = None
    skills: Optional[List[Skill]] = None

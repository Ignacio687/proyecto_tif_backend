from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

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

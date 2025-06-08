"""
Data Transfer Objects (DTOs) for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class UserRequest(BaseModel):
    """DTO for user assistant requests"""
    user_req: str = Field(description="User input for the assistant")


class GoogleAuthRequest(BaseModel):
    """DTO for Google OAuth authentication requests"""
    token: str = Field(description="Google OAuth ID token")


class Skill(BaseModel):
    """DTO for assistant skills"""
    name: str = Field(description="Name of the skill")
    action: str = Field(description="Action to be performed")
    params: Dict[str, Any] = Field(description="Parameters for the skill")


class ServerResponse(BaseModel):
    """DTO for server responses to user requests"""
    server_reply: str = Field(description="Server's reply message")
    app_params: Optional[List[Dict[str, bool]]] = Field(None, description="Application parameters")
    skills: Optional[List[Skill]] = Field(None, description="Skills to be executed")


class AuthResponse(BaseModel):
    """DTO for authentication responses"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(description="User ID")
    email: str = Field(description="User email")
    name: Optional[str] = Field(None, description="User name")


class SummarizedInteraction(BaseModel):
    """DTO for summarized interactions"""
    interaction_syntax: str = Field(description="Summary of the interaction")
    timestamp: datetime = Field(default_factory=utc_now, description="Timestamp of the summarized interaction")
    context_priority: int = Field(description="Priority of this interaction for context retention (1-100)")


class ConversationHistory(BaseModel):
    """DTO for conversation history responses"""
    conversations: List[Dict[str, Any]] = Field(description="List of conversations")
    total_count: int = Field(description="Total number of conversations")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")

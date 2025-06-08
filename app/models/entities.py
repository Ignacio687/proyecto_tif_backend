"""
Database entity models using Beanie ODM for MongoDB
"""
from beanie import Document
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.models.dtos import SummarizedInteraction


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class User(Document):
    """User entity representing registered users"""
    email: str = Field(description="User email address")
    google_id: Optional[str] = Field(None, description="Google OAuth ID")
    name: Optional[str] = Field(None, description="User full name")
    picture: Optional[str] = Field(None, description="User profile picture URL")
    created_at: datetime = Field(default_factory=utc_now, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether the user account is active")

    class Settings:
        name = "users"
        indexes = ["email", "google_id"]


class Conversation(Document):
    """Conversation entity representing user-assistant interactions"""
    user_id: str = Field(description="ID of the user who made the request")
    user_input: str = Field(description="User input for the assistant")
    server_reply: str = Field(description="Server's reply to the user")
    interaction_params: Optional[Dict[str, Any]] = Field(None, description="Additional interaction parameters")
    timestamp: datetime = Field(default_factory=utc_now, description="Timestamp of the interaction")

    class Settings:
        name = "conversations"
        indexes = ["user_id", "timestamp"]


class SummarizedContext(Document):
    """Summarized context entity for storing user's long-term memory"""
    user_id: str = Field(description="ID of the user this context belongs to")
    interactions: List[SummarizedInteraction] = Field(default_factory=list, description="List of summarized interactions")
    created_at: datetime = Field(default_factory=utc_now, description="Context creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Last context update timestamp")

    class Settings:
        name = "summarized_contexts"
        indexes = ["user_id"]

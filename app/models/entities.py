"""
Database entity models using Beanie ODM for MongoDB
"""
from beanie import Document
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class User(Document):
    """User entity representing registered users"""
    email: str = Field(description="User email address")
    # Google OAuth fields
    google_id: Optional[str] = Field(None, description="Google OAuth ID")
    # Email/username auth fields
    username: Optional[str] = Field(None, description="Username for email auth")
    password_hash: Optional[str] = Field(None, description="Hashed password for email auth")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    verification_code: Optional[str] = Field(None, description="Email verification code (6-8 chars)")
    verification_code_expires: Optional[datetime] = Field(None, description="Verification code expiration")
    # Password reset fields
    reset_code: Optional[str] = Field(None, description="Password reset code (6-8 chars)")
    reset_code_expires: Optional[datetime] = Field(None, description="Reset code expiration")
    # Common fields
    name: Optional[str] = Field(None, description="User full name")
    picture: Optional[str] = Field(None, description="User profile picture URL")
    created_at: datetime = Field(default_factory=utc_now, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether the user account is active")

    class Settings:
        name = "users"
        indexes = ["email", "google_id", "username"]


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


class KeyContext(Document):
    """Key context entity for storing individual context information pieces"""
    user_id: str = Field(description="ID of the user this context belongs to")
    relevant_info: str = Field(description="Key information about the user")
    context_priority: int = Field(description="Priority of this context for retention (1-100)")
    entry_number: Optional[int] = Field(None, description="Entry number for ordering")
    created_at: datetime = Field(default_factory=utc_now, description="Context creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Last context update timestamp")

    class Settings:
        name = "key_contexts"
        indexes = ["user_id", "context_priority"]

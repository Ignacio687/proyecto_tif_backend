"""
Data Transfer Objects (DTOs) for API requests and responses
"""
from pydantic import BaseModel, Field, EmailStr
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


class EmailRegisterRequest(BaseModel):
    """DTO for email registration requests"""
    email: EmailStr = Field(description="User email address")
    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=8, description="User password")
    name: Optional[str] = Field(None, max_length=100, description="User full name")


class EmailLoginRequest(BaseModel):
    """DTO for email login requests"""
    email_or_username: str = Field(description="Email address or username")
    password: str = Field(description="User password")


class EmailVerificationRequest(BaseModel):
    """DTO for email verification requests"""
    code: str = Field(min_length=6, max_length=8, description="Email verification code")


class PasswordResetRequest(BaseModel):
    """DTO for password reset requests"""
    email: EmailStr = Field(description="User email address")


class PasswordResetConfirmRequest(BaseModel):
    """DTO for password reset confirmation"""
    code: str = Field(min_length=6, max_length=8, description="Password reset code")
    new_password: str = Field(min_length=8, description="New password")


class ResendVerificationRequest(BaseModel):
    """DTO for resending verification code"""
    email: EmailStr = Field(description="User email address")


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
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(description="User ID")
    email: str = Field(description="User email")
    name: Optional[str] = Field(None, description="User name")
    is_verified: bool = Field(description="Whether email is verified")


class RefreshTokenRequest(BaseModel):
    """DTO for refresh token requests"""
    refresh_token: str = Field(description="Refresh token")


class ConversationHistory(BaseModel):
    """DTO for conversation history responses"""
    conversations: List[Dict[str, Any]] = Field(description="List of conversations")
    total_count: int = Field(description="Total number of conversations")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")

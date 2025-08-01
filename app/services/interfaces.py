"""
Service interfaces for business logic operations
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.models.entities import User
from app.models.dtos import AuthResponse, ServerResponse, SystemMessage


class AuthServiceInterface(ABC):
    """Interface for authentication services"""
    
    @abstractmethod
    async def authenticate_google_token(self, token: str) -> AuthResponse:
        """Authenticate user with Google token"""
        pass
    
    @abstractmethod
    async def register_with_email(self, email: str, username: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Register user with email and username"""
        pass
    
    @abstractmethod
    async def authenticate_email_login(self, email_or_username: str, password: str) -> AuthResponse:
        """Authenticate user with email/username and password"""
        pass
    
    @abstractmethod
    async def verify_email(self, code: str) -> Dict[str, Any]:
        """Verify user's email with verification code"""
        pass
    
    @abstractmethod
    async def resend_verification_code(self, email: str) -> Dict[str, Any]:
        """Resend verification code to user's email"""
        pass
    
    @abstractmethod
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset for user"""
        pass
    
    @abstractmethod
    async def confirm_password_reset(self, code: str, new_password: str) -> Dict[str, Any]:
        """Confirm password reset with code and new password"""
        pass
    
    @abstractmethod
    async def create_token_pair(self, user: User) -> Dict[str, str]:
        """Create both access and refresh tokens for user"""
        pass
    
    @abstractmethod
    async def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        pass
    
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        pass


class AssistantServiceInterface(ABC):
    """Interface for assistant services"""
    
    @abstractmethod
    async def handle_user_request(self, user_id: str, user_req: str, max_items: int = 10, 
                                 system_message: Optional[SystemMessage] = None) -> ServerResponse:
        """Handle user request and return assistant response"""
        pass
    
    @abstractmethod
    async def get_user_conversation_history(self, user_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get user's conversation history with pagination"""
        pass


class GeminiServiceInterface(ABC):
    """Interface for Gemini AI service"""
    
    @abstractmethod
    async def get_gemini_response(self, prompt: str, key_context_data: Optional[List[Dict[str, Any]]] = None, 
                                last_conversations: Optional[List[Dict[str, Any]]] = None, 
                                context_conversations: Optional[List[Dict[str, Any]]] = None, 
                                max_items: int = 10) -> Dict[str, Any]:
        """Get response from Gemini AI"""
        pass


class ContextServiceInterface(ABC):
    """Interface for context management service"""
    
    @abstractmethod
    def build_optimized_context(self, 
                              key_context_data: List[Dict[str, Any]], 
                              context_conversations: List[Dict[str, Any]],
                              fixed_context: str) -> str:
        """Build optimized context with character limits and smart prioritization"""
        pass
    
    @abstractmethod
    def calculate_context_stats(self, key_context_data: List[Dict[str, Any]], 
                               context_conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about context usage"""
        pass

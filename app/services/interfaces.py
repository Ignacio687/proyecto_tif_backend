"""
Service interfaces for business logic operations
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.models.entities import User
from app.models.dtos import AuthResponse, ServerResponse


class AuthServiceInterface(ABC):
    """Interface for authentication services"""
    
    @abstractmethod
    async def authenticate_google_token(self, token: str) -> AuthResponse:
        """Authenticate user with Google token"""
        pass
    
    @abstractmethod
    async def create_jwt_token(self, user: User) -> str:
        """Create JWT token for user"""
        pass
    
    @abstractmethod
    async def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        pass


class AssistantServiceInterface(ABC):
    """Interface for assistant services"""
    
    @abstractmethod
    async def handle_user_request(self, user_id: str, user_req: str, max_items: int = 10) -> ServerResponse:
        """Handle user request and return assistant response"""
        pass
    
    @abstractmethod
    async def get_user_conversation_history(self, user_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get user's conversation history with pagination"""
        pass


class GeminiServiceInterface(ABC):
    """Interface for Gemini AI service"""
    
    @abstractmethod
    async def get_gemini_response(self, prompt: str, summarized_context: Optional[List[Dict[str, Any]]] = None, 
                                last_conversations: Optional[List[Dict[str, Any]]] = None, 
                                context_conversations: Optional[List[Dict[str, Any]]] = None, 
                                max_items: int = 10) -> Dict[str, Any]:
        """Get response from Gemini AI"""
        pass
    
    @abstractmethod
    def build_and_update_summarized_context(self, summarized_context: List[Dict[str, Any]], 
                                           new_interaction: Optional[Dict[str, Any]] = None, 
                                           max_items: int = 10, 
                                           context_updates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Build and update summarized context"""
        pass

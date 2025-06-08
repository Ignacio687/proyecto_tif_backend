"""
Base repository interface for data access operations
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.entities import User, Conversation, SummarizedContext


class BaseRepository(ABC):
    """Abstract base repository interface"""
    
    @abstractmethod
    async def create(self, entity):
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str):
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, entity):
        """Update an existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str):
        """Delete an entity by ID"""
        pass


class UserRepositoryInterface(ABC):
    """Interface for user-specific repository operations"""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        pass
    
    @abstractmethod
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        pass


class ConversationRepositoryInterface(ABC):
    """Interface for conversation-specific repository operations"""
    
    @abstractmethod
    async def get_user_conversations(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Conversation]:
        """Get user's conversations with pagination"""
        pass
    
    @abstractmethod
    async def get_last_conversations(self, user_id: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Get user's last conversations"""
        pass
    
    @abstractmethod
    async def save_conversation(self, user_id: str, user_input: str, server_reply: str, 
                              interaction_params: Optional[Dict[str, Any]] = None) -> Conversation:
        """Save a new conversation"""
        pass


class SummarizedContextRepositoryInterface(ABC):
    """Interface for summarized context repository operations"""
    
    @abstractmethod
    async def get_user_context(self, user_id: str) -> Optional[SummarizedContext]:
        """Get user's summarized context"""
        pass
    
    @abstractmethod
    async def save_user_context(self, user_id: str, context_data: List[Dict[str, Any]]) -> SummarizedContext:
        """Save or update user's summarized context"""
        pass

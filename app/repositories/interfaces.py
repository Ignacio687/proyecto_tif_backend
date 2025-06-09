"""
Base repository interface for data access operations
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.entities import User, Conversation, KeyContext


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
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        pass
    
    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token"""
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


class KeyContextRepositoryInterface(ABC):
    """Interface for key context repository operations"""
    
    @abstractmethod
    async def get_user_key_contexts(self, user_id: str, limit: int = 10) -> List[KeyContext]:
        """Get user's key contexts"""
        pass
    
    @abstractmethod
    async def get_user_key_context_data(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's key context data as dict list"""
        pass
    
    @abstractmethod
    async def save_user_key_context(self, user_id: str, relevant_info: str, context_priority: int = 1) -> None:
        """Save a single new key context entry"""
        pass
    
    @abstractmethod
    async def update_key_context_priority(self, user_id: str, context_id: str, new_priority: int) -> bool:
        """Update priority of a specific key context entry by ID"""
        pass

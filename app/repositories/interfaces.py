"""
Base repository interface for data access
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
    async def get_by_verification_code(self, code: str) -> Optional[User]:
        """Get user by verification code"""
        pass
    
    @abstractmethod
    async def get_by_reset_code(self, code: str) -> Optional[User]:
        """Get user by password reset code"""
        pass
    
    @abstractmethod
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update an existing user"""
        pass


class ConversationRepositoryInterface(ABC):
    """Interface for conversation-specific repository operations"""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Conversation]:
        """Get conversations by user ID with pagination"""
        pass
    
    @abstractmethod
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Conversation:
        """Create a new conversation"""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        """Count conversations by user ID"""
        pass


class KeyContextRepositoryInterface(ABC):
    """Interface for key context-specific repository operations"""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[KeyContext]:
        """Get key contexts by user ID"""
        pass
    
    @abstractmethod
    async def create_key_context(self, context_data: Dict[str, Any]) -> KeyContext:
        """Create a new key context"""
        pass

    @abstractmethod
    async def update_key_context(self, context: KeyContext) -> KeyContext:
        """Update an existing key context"""
        pass

    @abstractmethod
    async def delete_by_id(self, context_id: str) -> bool:
        """Delete a key context by ID"""
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> bool:
        """Delete all key contexts for a user"""
        pass


class MongoRepositoryInterface(ABC):
    """Interface for MongoDB-specific operations"""
    
    @abstractmethod
    async def init_db(self, models: List):
        """Initialize database with model schemas"""
        pass

    @abstractmethod
    async def close_db(self):
        """Close database connection"""
        pass

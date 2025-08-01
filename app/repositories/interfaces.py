"""
Repository interfaces for data access
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
    async def get_user_conversations(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Conversation]:
        """Get user's conversations with pagination"""
        pass
    
    @abstractmethod
    async def get_optimized_conversations(self, user_id: str, max_chars: int = 2000) -> List[Dict[str, Any]]:
        """Get conversations optimized for character limits"""
        pass
    
    @abstractmethod
    async def save_conversation(self, user_id: str, user_input: str, server_reply: str, 
                              interaction_params: Optional[Dict[str, Any]] = None) -> Conversation:
        """Save a new conversation"""
        pass

    @abstractmethod
    async def count_user_conversations(self, user_id: str) -> int:
        """Count total conversations for a user"""
        pass

    @abstractmethod
    async def update_conversation_reply(self, conversation_id: str, new_server_reply: str) -> bool:
        """Update the server_reply of a specific conversation"""
        pass


class KeyContextRepositoryInterface(ABC):
    """Interface for key context-specific repository operations"""
    
    @abstractmethod
    async def get_user_key_contexts(self, user_id: str, limit: int = 10) -> List[KeyContext]:
        """Get user's key contexts ordered by priority"""
        pass
    
    @abstractmethod
    async def save_user_key_context(self, user_id: str, relevant_info: str, context_priority: int = 1) -> None:
        """Save a single new key context entry"""
        pass

    @abstractmethod
    async def update_key_context_priority(self, user_id: str, context_id: str, new_priority: int) -> bool:
        """Update priority of a specific key context entry by ID"""
        pass

    @abstractmethod
    async def delete_low_priority_contexts(self, user_id: str) -> None:
        """Delete contexts with priority 0"""
        pass

    @abstractmethod
    async def cleanup_old_contexts(self, user_id: str, max_items: int = 10) -> None:
        """Remove only contexts with priority 0 if exceeding max_items limit"""
        pass

    @abstractmethod
    async def get_optimized_key_contexts(self, user_id: str, max_chars: int = 1500, min_priority: int = 1) -> List[Dict[str, Any]]:
        """Get key contexts optimized for character limits and priority"""
        pass
    
    @abstractmethod
    async def get_context_summary_stats(self, user_id: str) -> Dict[str, Any]:
        """Get summary statistics about user's context"""
        pass

    @abstractmethod
    async def cleanup_duplicate_contexts(self, user_id: str) -> int:
        """Remove duplicate key contexts, keeping the most recent one"""
        pass

"""
Conversation repository implementation using Beanie ODM
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.models.entities import Conversation
from app.repositories.interfaces import ConversationRepositoryInterface
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class ConversationRepository(ConversationRepositoryInterface):
    """Repository for conversation operations"""
    
    async def get_user_conversations(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Conversation]:
        """Get user's conversations with pagination"""
        try:
            conversations = await Conversation.find(
                Conversation.user_id == user_id
            ).sort("-timestamp").skip(skip).limit(limit).to_list()
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []
    
    async def get_last_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's last conversations"""
        try:
            conversations = await Conversation.find(
                Conversation.user_id == user_id
            ).sort("-timestamp").limit(limit).to_list()
            
            # Convert to dict format for compatibility with existing code
            return [
                {
                    "user_input": conv.user_input,
                    "server_reply": conv.server_reply,
                    "timestamp": conv.timestamp,
                    "interaction_params": conv.interaction_params
                }
                for conv in conversations
            ]
        except Exception as e:
            logger.error(f"Error getting last conversations for user {user_id}: {e}")
            return []
    
    async def save_conversation(self, user_id: str, user_input: str, server_reply: str, 
                              interaction_params: Optional[Dict[str, Any]] = None) -> Conversation:
        """Save a new conversation"""
        try:
            conversation = Conversation(
                user_id=user_id,
                user_input=user_input,
                server_reply=server_reply,
                interaction_params=interaction_params,
                timestamp=utc_now()
            )
            await conversation.create()
            logger.debug(f"Saved conversation for user {user_id}")
            return conversation
        except Exception as e:
            logger.error(f"Error saving conversation for user {user_id}: {e}")
            raise
    
    async def count_user_conversations(self, user_id: str) -> int:
        """Count total conversations for a user"""
        try:
            return await Conversation.find(Conversation.user_id == user_id).count()
        except Exception as e:
            logger.error(f"Error counting conversations for user {user_id}: {e}")
            return 0

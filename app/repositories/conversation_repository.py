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

    async def update_conversation_reply(self, conversation_id: str, new_server_reply: str) -> bool:
        """Update the server_reply of a specific conversation"""
        try:
            from bson import ObjectId
            # Find and update the conversation
            conversation = await Conversation.get(ObjectId(conversation_id))
            if conversation:
                conversation.server_reply = new_server_reply
                await conversation.save()
                logger.debug(f"Updated conversation {conversation_id} with new server reply")
                return True
            else:
                logger.warning(f"Conversation {conversation_id} not found for update")
                return False
        except Exception as e:
            logger.error(f"Error updating conversation {conversation_id}: {e}")
            return False

    async def get_optimized_conversations(self, user_id: str, max_chars: int = 2000) -> List[Dict[str, Any]]:
        """Get conversations optimized for context length"""
        try:
            conversations = await Conversation.find(
                Conversation.user_id == user_id
            ).sort("-timestamp").to_list()
            
            optimized_conversations = []
            total_chars = 0
            
            for conv in conversations:
                # Format conversation for context
                conversation_text = f"User: {conv.user_input}\nAssistant: {conv.server_reply}"
                conv_chars = len(conversation_text)
                
                # Check if adding this conversation would exceed the limit
                if total_chars + conv_chars > max_chars:
                    break
                
                optimized_conversations.append({
                    "user_input": conv.user_input,
                    "server_reply": conv.server_reply,
                    "timestamp": conv.timestamp,
                    "interaction_params": conv.interaction_params,
                    "char_count": conv_chars
                })
                
                total_chars += conv_chars
            
            logger.debug(f"Retrieved {len(optimized_conversations)} conversations for context ({total_chars} chars)")
            return optimized_conversations
            
        except Exception as e:
            logger.error(f"Error getting optimized conversations for user {user_id}: {e}")
            return []

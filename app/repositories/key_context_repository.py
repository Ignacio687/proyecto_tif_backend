"""
Key context repository implementation using Beanie ODM
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.models.entities import KeyContext
from app.repositories.interfaces import KeyContextRepositoryInterface
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class KeyContextRepository(KeyContextRepositoryInterface):
    """Repository for key context operations"""
    
    async def get_user_key_contexts(self, user_id: str, limit: int = 10) -> List[KeyContext]:
        """Get user's key contexts ordered by priority"""
        try:
            contexts = await KeyContext.find(
                KeyContext.user_id == user_id
            ).sort("-context_priority", "-updated_at").limit(limit).to_list()
            return contexts
        except Exception as e:
            logger.error(f"Error getting key contexts for user {user_id}: {e}")
            return []
    
    async def get_user_key_context_data(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's key context data as dict list for compatibility"""
        try:
            contexts = await self.get_user_key_contexts(user_id, limit)
            # Add entry numbers and convert to dict format
            return [
                {
                    "relevant_info": context.relevant_info,
                    "timestamp": context.updated_at,
                    "context_priority": context.context_priority,
                    "entry_number": idx + 1
                }
                for idx, context in enumerate(contexts)
            ]
        except Exception as e:
            logger.error(f"Error getting context data for user {user_id}: {e}")
            return []
    
    async def save_user_key_context(self, user_id: str, relevant_info: str, context_priority: int = 1) -> None:
        """Save a single new key context entry"""
        try:
            context = KeyContext(
                user_id=user_id,
                relevant_info=relevant_info,
                context_priority=context_priority,
                entry_number=None,  # Will be set dynamically when needed
                created_at=utc_now(),
                updated_at=utc_now()
            )
            await context.create()
            
            logger.debug(f"Saved new key context for user {user_id}: {relevant_info[:50]}...")
        except Exception as e:
            logger.error(f"Error saving key context for user {user_id}: {e}")
            raise
    
    async def update_key_context_priority(self, user_id: str, context_id: str, new_priority: int) -> bool:
        """Update priority of a specific key context entry by ID"""
        try:
            context = await KeyContext.get(context_id)
            if context and context.user_id == user_id:
                context.context_priority = new_priority
                context.updated_at = utc_now()
                await context.save()
                logger.debug(f"Updated key context priority for user {user_id}, context {context_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating key context priority for user {user_id}, context {context_id}: {e}")
            return False
    
    async def delete_low_priority_contexts(self, user_id: str) -> None:
        """Delete contexts with priority 0"""
        try:
            await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority == 0
            ).delete()
            logger.debug(f"Deleted low priority contexts for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting low priority contexts for user {user_id}: {e}")
    
    async def cleanup_old_contexts(self, user_id: str, max_items: int = 10) -> None:
        """Remove only contexts with priority 0 if exceeding max_items limit"""
        try:
            # Only delete contexts with priority 0 (marked for deletion)
            zero_priority_contexts = await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority == 0
            ).to_list()
            
            if zero_priority_contexts:
                for context in zero_priority_contexts:
                    await context.delete()
                logger.debug(f"Cleaned up {len(zero_priority_contexts)} zero-priority contexts for user {user_id}")
            else:
                logger.debug(f"No zero-priority contexts to clean up for user {user_id}")
        except Exception as e:
            logger.error(f"Error cleaning up contexts for user {user_id}: {e}")

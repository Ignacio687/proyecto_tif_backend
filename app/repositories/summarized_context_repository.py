"""
Summarized context repository implementation using Beanie ODM
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.models.entities import SummarizedContext
from app.repositories.interfaces import SummarizedContextRepositoryInterface
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class SummarizedContextRepository(SummarizedContextRepositoryInterface):
    """Repository for summarized context operations"""
    
    async def get_user_context(self, user_id: str) -> Optional[SummarizedContext]:
        """Get user's summarized context"""
        try:
            return await SummarizedContext.find_one(SummarizedContext.user_id == user_id)
        except Exception as e:
            logger.error(f"Error getting summarized context for user {user_id}: {e}")
            return None
    
    async def get_user_context_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's summarized context data as dict list for compatibility"""
        try:
            context = await self.get_user_context(user_id)
            if context and context.interactions:
                # Convert SummarizedInteraction objects to dict format
                return [
                    {
                        "relevant_info": interaction.interaction_syntax,
                        "timestamp": interaction.timestamp,
                        "context_priority": interaction.context_priority
                    }
                    for interaction in context.interactions
                ]
            return []
        except Exception as e:
            logger.error(f"Error getting context data for user {user_id}: {e}")
            return []
    
    async def save_user_context(self, user_id: str, context_data: List[Dict[str, Any]]) -> SummarizedContext:
        """Save or update user's summarized context"""
        try:
            # Convert dict data to SummarizedInteraction objects
            from app.models.dtos import SummarizedInteraction
            interactions = [
                SummarizedInteraction(
                    interaction_syntax=item.get("relevant_info", ""),
                    timestamp=item.get("timestamp", utc_now()),
                    context_priority=item.get("context_priority", 1)
                )
                for item in context_data
            ]
            
            # Find existing context or create new one
            context = await self.get_user_context(user_id)
            if context:
                context.interactions = interactions
                context.updated_at = utc_now()
                await context.save()
                logger.debug(f"Updated summarized context for user {user_id}")
            else:
                context = SummarizedContext(
                    user_id=user_id,
                    interactions=interactions,
                    created_at=utc_now(),
                    updated_at=utc_now()
                )
                await context.create()
                logger.debug(f"Created new summarized context for user {user_id}")
            
            return context
        except Exception as e:
            logger.error(f"Error saving summarized context for user {user_id}: {e}")
            raise

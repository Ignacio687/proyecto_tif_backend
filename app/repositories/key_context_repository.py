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
    
    async def get_user_key_contexts(self, user_id: str, limit: int = 30) -> List[KeyContext]:
        """Get user's key contexts ordered by priority"""
        try:
            contexts = await KeyContext.find(
                KeyContext.user_id == user_id
            ).sort("-context_priority", "-updated_at").limit(limit).to_list()
            return contexts
        except Exception as e:
            logger.error(f"Error getting key contexts for user {user_id}: {e}")
            return []
    
    async def save_user_key_context(self, user_id: str, relevant_info: str, context_priority: int = 1) -> None:
        """Save a single new key context entry, avoiding duplicates"""
        try:
            # Check for existing similar context first
            existing_context = await self._find_similar_context(user_id, relevant_info)
            
            if existing_context:
                # Update existing context priority if new one is higher, and refresh timestamp
                if context_priority > existing_context.context_priority:
                    existing_context.context_priority = context_priority
                    existing_context.updated_at = utc_now()
                    await existing_context.save()
                    logger.debug(f"Updated existing key context priority for user {user_id}: {relevant_info[:50]}...")
                else:
                    # Just refresh the timestamp to show it's still relevant
                    existing_context.updated_at = utc_now()
                    await existing_context.save()
                    logger.debug(f"Refreshed existing key context timestamp for user {user_id}: {relevant_info[:50]}...")
                return
            
            # Create new context only if no similar one exists
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

    async def _find_similar_context(self, user_id: str, relevant_info: str) -> Optional[KeyContext]:
        """Find existing context that is similar to avoid duplicates"""
        try:
            # Normalize the text for comparison
            normalized_info = relevant_info.strip().lower()
            
            # Get all contexts for this user
            existing_contexts = await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority > 0  # Only active contexts
            ).to_list()
            
            # Check for exact matches or very similar content
            for context in existing_contexts:
                existing_normalized = context.relevant_info.strip().lower()
                
                # Exact match
                if existing_normalized == normalized_info:
                    return context
                
                # Very similar (same words, different punctuation)
                existing_words = set(existing_normalized.replace('.', '').replace(',', '').split())
                new_words = set(normalized_info.replace('.', '').replace(',', '').split())
                
                # If 90% of words overlap, consider it duplicate
                if len(existing_words & new_words) / max(len(existing_words), len(new_words)) >= 0.9:
                    return context
            
            return None
        except Exception as e:
            logger.error(f"Error finding similar context for user {user_id}: {e}")
            return None

    async def cleanup_duplicate_contexts(self, user_id: str) -> int:
        """Remove duplicate key contexts, keeping the most recent one"""
        try:
            # Get all contexts for this user
            all_contexts = await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority > 0
            ).sort("-updated_at").to_list()
            
            if not all_contexts:
                return 0
            
            # Group contexts by normalized content
            content_groups = {}
            for context in all_contexts:
                normalized = context.relevant_info.strip().lower().replace('.', '').replace(',', '')
                normalized_words = ' '.join(sorted(normalized.split()))  # Sort words for better matching
                
                if normalized_words not in content_groups:
                    content_groups[normalized_words] = []
                content_groups[normalized_words].append(context)
            
            # Remove duplicates (keep the most recent one in each group)
            removed_count = 0
            for content, contexts in content_groups.items():
                if len(contexts) > 1:
                    # Keep the first one (most recent due to sorting), remove the rest
                    for duplicate_context in contexts[1:]:
                        await duplicate_context.delete()
                        removed_count += 1
                        logger.debug(f"Removed duplicate context: {duplicate_context.relevant_info[:50]}...")
            
            logger.info(f"Cleaned up {removed_count} duplicate contexts for user {user_id}")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate contexts for user {user_id}: {e}")
            return 0
    
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

    async def get_optimized_key_contexts(self, user_id: str, max_chars: int = 1500, min_priority: int = 1) -> List[Dict[str, Any]]:
        """Get key contexts optimized for character length"""
        try:
            contexts = await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority >= min_priority
            ).sort("-context_priority", "-updated_at").to_list()
            
            optimized_contexts = []
            total_chars = 0
            
            for idx, context in enumerate(contexts):
                # Calculate character count for this context entry
                context_text = f"- {context.relevant_info}"
                context_chars = len(context_text)
                
                # Check if adding this context would exceed the limit
                if total_chars + context_chars > max_chars:
                    logger.debug(f"Context limit reached at entry {idx + 1}, truncating")
                    break
                
                optimized_contexts.append({
                    "relevant_info": context.relevant_info,
                    "timestamp": context.updated_at,
                    "context_priority": context.context_priority,
                    "entry_number": idx + 1,
                    "char_count": context_chars
                })
                
                total_chars += context_chars
            
            logger.debug(f"Retrieved {len(optimized_contexts)} key contexts for user {user_id} ({total_chars} chars)")
            return optimized_contexts
            
        except Exception as e:
            logger.error(f"Error getting optimized key contexts for user {user_id}: {e}")
            return []

    async def get_context_summary_stats(self, user_id: str) -> Dict[str, Any]:
        """Get summary statistics for user's context"""
        try:
            total_contexts = await KeyContext.find(KeyContext.user_id == user_id).count()
            high_priority_contexts = await KeyContext.find(
                KeyContext.user_id == user_id,
                KeyContext.context_priority >= 50
            ).count()
            
            return {
                "total_contexts": total_contexts,
                "high_priority_contexts": high_priority_contexts,
                "context_usage": f"{total_contexts} contexts, {high_priority_contexts} high priority"
            }
        except Exception as e:
            logger.error(f"Error getting context summary stats for user {user_id}: {e}")
            return {"total_contexts": 0, "high_priority_contexts": 0, "context_usage": "0 contexts"}

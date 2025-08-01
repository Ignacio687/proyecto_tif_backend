"""
Assistant service implementation for handling user interactions
"""
import json
from typing import Dict, Any, Optional, List
from app.models.dtos import ServerResponse, SystemMessage
from app.services.interfaces import AssistantServiceInterface
from app.logger import logger


class AssistantService(AssistantServiceInterface):
    """Service for handling assistant operations"""
    
    def __init__(self, conversation_repository=None, key_context_repository=None, 
                 gemini_service=None, context_service=None):
        # Use dependency injection to avoid creating new instances each time
        if conversation_repository is None:
            from app.repositories.conversation_repository import ConversationRepository
            conversation_repository = ConversationRepository()
        if key_context_repository is None:
            from app.repositories.key_context_repository import KeyContextRepository
            key_context_repository = KeyContextRepository()
        if context_service is None:
            from app.services.context_service import ContextService
            context_service = ContextService()
        if gemini_service is None:
            from app.services.gemini_service import GeminiService
            gemini_service = GeminiService(context_service)
            
        self.conversation_repository = conversation_repository
        self.key_context_repository = key_context_repository
        self.gemini_service = gemini_service
        self.context_service = context_service
    
    async def handle_user_request(self, user_id: str, user_req: str, max_items: int = 10, 
                                 system_message: Optional[SystemMessage] = None) -> ServerResponse:
        """Handle user request and return assistant response"""
        try:
            # Get user's conversation history using the context service's optimized method
            last_conversations = await self.conversation_repository.get_optimized_conversations(user_id)
            
            # Get user's key contexts using the context service's optimized method
            key_context_data = await self.key_context_repository.get_optimized_key_contexts(user_id)
            
            # Create mapping from entry_number to context_id for efficient updates later
            key_contexts_full = await self.key_context_repository.get_user_key_contexts(user_id)
            entry_to_context_map = {idx + 1: str(context.id) for idx, context in enumerate(key_contexts_full)}
            
            # Handle patching if requested
            if system_message and system_message.patch_last:
                # Create an enhanced prompt with additional context
                enhanced_prompt = f"PATCH REQUEST: The user said '{user_req}' but additional context is now available. "
                
                # Add contacts list if provided
                if system_message.contacts_list:
                    contacts_str = ", ".join(system_message.contacts_list)
                    enhanced_prompt += f"Available contacts: {contacts_str}. "
                
                logger.info(f"Patch requested. Original query: '{user_req}', Additional context provided")
                
                # Get response with enhanced context for patch request
                gemini_reply = await self.gemini_service.get_gemini_response(
                    enhanced_prompt,
                    key_context_data=key_context_data,
                    last_conversations=last_conversations,
                    context_conversations=last_conversations,
                    max_items=max_items
                )
                
                # Update the last conversation in database with the patched response
                await self._update_last_conversation_with_patch(user_id, gemini_reply.get('server_reply', ''))
                logger.info(f"Updated last conversation for user {user_id} with patched response")
            else:
                # Get Gemini response using the new architecture for normal requests
                gemini_reply = await self.gemini_service.get_gemini_response(
                    user_req,
                    key_context_data=key_context_data,
                    last_conversations=last_conversations,
                    context_conversations=last_conversations,
                    max_items=max_items
                )
                
                # Save the conversation normally only if it's not a patch request
                await self.conversation_repository.save_conversation(
                    user_id=user_id,
                    user_input=user_req,
                    server_reply=gemini_reply.get('server_reply', ''),
                    interaction_params=gemini_reply.get('interaction_params')
                )
            
            # Extract and save key context information from the interaction
            # 1. Process context updates (priority changes for existing entries) using the mapping
            context_updates = gemini_reply.get('context_updates')
            if context_updates and isinstance(context_updates, list):
                for update in context_updates:
                    if isinstance(update, dict) and 'entry_number' in update and 'new_priority' in update:
                        entry_number = update['entry_number']
                        new_priority = update['new_priority']
                        
                        # Use the mapping to get the context_id efficiently
                        context_id = entry_to_context_map.get(entry_number)
                        if context_id:
                            success = await self.key_context_repository.update_key_context_priority(
                                user_id=user_id,
                                context_id=context_id,
                                new_priority=new_priority
                            )
                            if success:
                                logger.debug(f"Updated key context priority for user {user_id}, entry {entry_number} (ID: {context_id}) to priority {new_priority}")
                        else:
                            logger.warning(f"Invalid entry_number {entry_number} for user {user_id} context updates")
            
            # 2. Save the relevant info from the current interaction's interaction_params
            interaction_params = gemini_reply.get('interaction_params')
            if (interaction_params and 
                interaction_params.get('relevant_for_context') and 
                interaction_params.get('relevant_info')):
                await self.key_context_repository.save_user_key_context(
                    user_id=user_id,
                    relevant_info=interaction_params['relevant_info'],
                    context_priority=interaction_params.get('context_priority', 1)
                )
                logger.debug(f"Saved current interaction key context for user {user_id}: {interaction_params['relevant_info'][:50]}...")
            
            # Clean up zero-priority key contexts to maintain performance
            await self.key_context_repository.cleanup_old_contexts(user_id, max_items)
            
            # Clean up duplicate contexts periodically (every 10th request)
            import random
            if random.randint(1, 100) == 1:  # 1% chance
                removed_count = await self.key_context_repository.cleanup_duplicate_contexts(user_id)
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} duplicate contexts for user {user_id}")
            
            # Return structured response
            return ServerResponse(
                server_reply=gemini_reply.get('server_reply', ''),
                app_params=gemini_reply.get('app_params'),
                skills=gemini_reply.get('skills')
            )
            
        except Exception as e:
            logger.error(f"Error handling user request for user {user_id}: {e}")
            raise
    
    async def get_user_conversation_history(self, user_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get user's conversation history with pagination"""
        try:
            skip = (page - 1) * page_size
            conversations = await self.conversation_repository.get_user_conversations(
                user_id, limit=page_size, skip=skip
            )
            
            total_count = await self.conversation_repository.count_user_conversations(user_id)
            
            # Convert to dict format for response
            conversation_list = [
                {
                    "user_input": conv.user_input,
                    "server_reply": conv.server_reply,
                    "timestamp": conv.timestamp
                }
                for conv in conversations
            ]
            
            return {
                "conversations": conversation_list,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history for user {user_id}: {e}")
            raise

    async def _update_last_conversation_with_patch(self, user_id: str, patched_server_reply: str) -> None:
        """Update the last conversation in database with the patched response"""
        try:
            # Get the most recent conversation for this user
            recent_conversations = await self.conversation_repository.get_user_conversations(
                user_id, limit=1, skip=0
            )
            
            if recent_conversations:
                last_conversation = recent_conversations[0]
                # Update the server_reply of the last conversation with the patched response
                success = await self.conversation_repository.update_conversation_reply(
                    conversation_id=str(last_conversation.id),
                    new_server_reply=patched_server_reply
                )
                if success:
                    logger.info(f"Successfully updated last conversation {last_conversation.id} with patched response")
                else:
                    logger.error(f"Failed to update last conversation {last_conversation.id} with patched response")
            else:
                logger.warning(f"No conversations found for user {user_id} to patch")
                
        except Exception as e:
            logger.error(f"Error updating last conversation with patch for user {user_id}: {e}")
            # Don't raise exception to avoid breaking the main flow

"""
Assistant service implementation for handling user interactions
"""
from typing import Dict, Any
from app.models.dtos import ServerResponse
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.key_context_repository import KeyContextRepository
from app.services.interfaces import AssistantServiceInterface
from app.services.gemini_service import GeminiService
from app.logger import logger


class AssistantService(AssistantServiceInterface):
    """Service for handling assistant operations"""
    
    def __init__(self):
        self.conversation_repository = ConversationRepository()
        self.key_context_repository = KeyContextRepository()
        self.gemini_service = GeminiService()
    
    async def handle_user_request(self, user_id: str, user_req: str, max_items: int = 10) -> ServerResponse:
        """Handle user request and return assistant response"""
        try:
            # Get user's conversation history
            last_conversations = await self.conversation_repository.get_last_conversations(user_id)
            
            # Get user's key contexts and build mapping for efficient updates
            key_contexts = await self.key_context_repository.get_user_key_contexts(user_id)
            
            # Create mapping from entry_number to context_id for efficient updates later
            entry_to_context_map = {idx + 1: str(context.id) for idx, context in enumerate(key_contexts)}
            
            # Convert to data format for Gemini with temporary entry numbers
            key_context_data = [
                {
                    "relevant_info": context.relevant_info,
                    "timestamp": context.updated_at,
                    "context_priority": context.context_priority,
                    "entry_number": idx + 1
                }
                for idx, context in enumerate(key_contexts)
            ]
            
            # Get Gemini response
            gemini_reply = await self.gemini_service.get_gemini_response(
                user_req,
                key_context_data=key_context_data,
                last_conversations=last_conversations,
                context_conversations=last_conversations,
                max_items=max_items
            )
            
            # Save the conversation
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

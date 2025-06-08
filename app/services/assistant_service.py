"""
Assistant service implementation for handling user interactions
"""
from typing import Dict, Any
from app.models.dtos import ServerResponse
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.summarized_context_repository import SummarizedContextRepository
from app.services.interfaces import AssistantServiceInterface
from app.services.gemini_service import GeminiService
from app.logger import logger


class AssistantService(AssistantServiceInterface):
    """Service for handling assistant operations"""
    
    def __init__(self):
        self.conversation_repository = ConversationRepository()
        self.context_repository = SummarizedContextRepository()
        self.gemini_service = GeminiService()
    
    async def handle_user_request(self, user_id: str, user_req: str, max_items: int = 10) -> ServerResponse:
        """Handle user request and return assistant response"""
        try:
            # Get user's conversation history
            last_conversations = await self.conversation_repository.get_last_conversations(user_id)
            
            # Get user's summarized context
            summarized_context = await self.context_repository.get_user_context_data(user_id)
            
            # Get Gemini response
            gemini_reply = await self.gemini_service.get_gemini_response(
                user_req,
                summarized_context=summarized_context,
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
            
            # Update summarized context
            new_interaction = {
                'interaction_params': gemini_reply.get('interaction_params', {}),
                'server_reply': gemini_reply.get('server_reply', ''),
                'user_input': user_req
            }
            
            context_updates = gemini_reply.get('context_updates')
            updated_summarized_context = self.gemini_service.build_and_update_summarized_context(
                summarized_context, 
                new_interaction=new_interaction, 
                max_items=max_items, 
                context_updates=context_updates
            )
            
            await self.context_repository.save_user_context(user_id, updated_summarized_context)
            
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
                    "id": str(conv.id),
                    "user_input": conv.user_input,
                    "server_reply": conv.server_reply,
                    "timestamp": conv.timestamp,
                    "interaction_params": conv.interaction_params
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

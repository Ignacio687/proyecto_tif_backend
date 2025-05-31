from fastapi import APIRouter, HTTPException
from app.models.request_response import UserRequest, ServerResponse
from app.services.gemini_service import GeminiService
from app.logger import logger
from app.repositories.mongo_repository import MongoRepository

router = APIRouter()

gemini_service = GeminiService()
mongo_repository = MongoRepository()

@router.post("/assistant", response_model=ServerResponse)
async def assistant_endpoint(request: UserRequest):
    """
    Endpoint to handle user requests and provide responses from the Gemini service.
    """
    try:
        # Get last 20 conversations for context
        last_conversations = await mongo_repository.get_last_conversations()
        # Get summarized context from DB
        summarized_context = await mongo_repository.get_summarized_context()
        # Use summarized context and conversations in Gemini
        gemini_reply = await gemini_service.get_gemini_response(
            request.user_req,
            context_conversations=last_conversations
        )
        # Save the interaction (timestamp is generated here)
        await mongo_repository.save_conversation(
            request.user_req,
            gemini_reply.get('server_reply', ''),
            gemini_reply.get('interaction_params')
        )
        # Update summarized context after Gemini response
        new_interaction = {
            'interaction_params': gemini_reply.get('interaction_params', {}),
            'server_reply': gemini_reply.get('server_reply', ''),
            'user_input': request.user_req
        }
        updated_summarized_context = gemini_service.build_and_update_summarized_context(
            last_conversations, new_interaction=new_interaction
        )
        await gemini_service.save_summarized_context(updated_summarized_context, mongo_repository)
        response = ServerResponse(
            server_reply=gemini_reply.get('server_reply', ''),
            app_params=gemini_reply.get('app_params'),
            skills=gemini_reply.get('skills')
        )
        logger.info(f"Response sent: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in assistant_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

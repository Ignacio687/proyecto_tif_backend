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
        gemini_reply = await gemini_service.get_gemini_response(request.user_req, context_conversations=last_conversations)
        # Save the interaction
        await mongo_repository.save_conversation(request.user_req, gemini_reply)
        response = ServerResponse(
            server_reply=gemini_reply,
            app_params=None,
            skills=None
        )
        logger.info(f"Response sent: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in assistant_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

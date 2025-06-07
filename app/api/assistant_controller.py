from fastapi import APIRouter, HTTPException
from app.models.request_response import UserRequest, ServerResponse
from app.services.gemini_service import GeminiService
from app.logger import logger
from app.config import settings
import traceback

router = APIRouter()

gemini_service = GeminiService()

@router.post("/assistant", response_model=ServerResponse)
async def assistant_endpoint(request: UserRequest):
    """
    Endpoint to handle user requests and provide responses from the Gemini service.
    """
    try:
        response = await gemini_service.handle_user_request(request.user_req)
        logger.info(f"Response sent: {response}")
        return response
    except Exception as e:
        # Always print the complete error to console
        logger.error(f"Error in assistant_endpoint: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # If in DEBUG mode, return the complete stack trace
        if settings.LOG_LEVEL.upper() == "DEBUG":
            error_detail = f"Error: {str(e)}\n\nStack trace:\n{traceback.format_exc()}"
            raise HTTPException(status_code=500, detail=error_detail)
        else:
            # In any other mode, only return a generic message
            raise HTTPException(status_code=500, detail="Internal server error")

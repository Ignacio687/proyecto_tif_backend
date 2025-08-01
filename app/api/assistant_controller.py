from fastapi import APIRouter, HTTPException, Depends
from app.models.dtos import UserRequest, ServerResponse
from app.services.assistant_service import AssistantService
from app.api.auth_controller import get_current_user
from app.dependencies import get_assistant_service
from app.logger import logger
from app.config import settings
import traceback

router = APIRouter()

@router.post("/assistant", response_model=ServerResponse)
async def assistant_endpoint(
    request: UserRequest,
    current_user: dict = Depends(get_current_user),
    assistant_service: AssistantService = Depends(get_assistant_service)
):
    """
    Endpoint to handle user requests and provide responses from the assistant service.
    Requires JWT authentication.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
            
        response = await assistant_service.handle_user_request(
            user_id, 
            request.user_req, 
            system_message=request.system_message
        )
        logger.info(f"Response sent for user {user_id}: {response.server_reply[:100]}...")
        return response
    except HTTPException:
        raise
    except Exception as e:
        # Always print the complete error to console
        logger.error(f"Error in assistant_endpoint for user {current_user.get('user_id', 'unknown')}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # If in DEBUG mode, return the complete stack trace
        if settings.DEBUG:
            error_detail = f"Error: {str(e)}\n\nStack trace:\n{traceback.format_exc()}"
            raise HTTPException(status_code=500, detail=error_detail)
        else:
            # In any other mode, only return a generic message
            raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/conversations")
async def get_conversation_history(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user),
    assistant_service: AssistantService = Depends(get_assistant_service)
):
    """
    Get user's conversation history with pagination.
    Requires JWT authentication.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
            
        history = await assistant_service.get_user_conversation_history(
            user_id, page, page_size
        )
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history for user {current_user.get('user_id', 'unknown')}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")

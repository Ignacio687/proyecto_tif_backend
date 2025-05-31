from fastapi import APIRouter, HTTPException
from app.models.request_response import UserRequest, ServerResponse
from app.services.gemini_service import GeminiService
from app.logger import logger

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
        logger.error(f"Error in assistant_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

"""
Authentication API controller
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.dtos import GoogleAuthRequest, AuthResponse
from app.services.auth_service import AuthService
from app.dependencies import get_auth_service
from app.logger import logger
import traceback

router = APIRouter()
security = HTTPBearer()

@router.post("/google", response_model=AuthResponse)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with Google OAuth token
    """
    try:
        response = await auth_service.authenticate_google_token(request.token)
        logger.info(f"User authenticated successfully: {response.email}")
        return response
    except ValueError as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in Google authentication: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify JWT token and return user information
    """
    try:
        token = credentials.credentials
        payload = await auth_service.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "valid": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

# Dependency for getting current user from JWT token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Get current user from JWT token (dependency for protected endpoints)
    """
    try:
        token = credentials.credentials
        payload = await auth_service.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

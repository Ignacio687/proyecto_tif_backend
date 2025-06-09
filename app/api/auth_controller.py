"""
Authentication API controller
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.dtos import (
    GoogleAuthRequest, AuthResponse, EmailRegisterRequest, 
    EmailLoginRequest, EmailVerificationRequest
)
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

@router.post("/register", response_model=dict)
async def register_with_email(
    request: EmailRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register user with email and username
    """
    try:
        result = await auth_service.register_with_email(
            email=request.email,
            username=request.username,
            password=request.password,
            name=request.name
        )
        logger.info(f"User registered successfully: {request.email}")
        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": result.get("user_id")
        }
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in email registration: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service error"
        )

@router.post("/login", response_model=AuthResponse)
async def login_with_email(
    request: EmailLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login user with email/username and password
    """
    try:
        response = await auth_service.authenticate_email_login(
            email_or_username=request.email_or_username,
            password=request.password
        )
        logger.info(f"User logged in successfully: {response.email}")
        return response
    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in email login: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/verify-email", response_model=dict)
async def verify_email(
    request: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify user's email address with verification token
    """
    try:
        result = await auth_service.verify_email(request.token)
        logger.info(f"Email verified successfully for user: {result.get('email')}")
        return {
            "message": "Email verified successfully. You can now log in.",
            "verified": True
        }
    except ValueError as e:
        logger.warning(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in email verification: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification service error"
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

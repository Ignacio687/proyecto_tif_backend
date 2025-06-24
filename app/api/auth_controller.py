"""
Authentication API controller
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.dtos import (
    GoogleAuthRequest, AuthResponse, EmailRegisterRequest, 
    EmailLoginRequest, EmailVerificationRequest, PasswordResetRequest,
    PasswordResetConfirmRequest, ResendVerificationRequest, RefreshTokenRequest
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
            "token_type": payload.get("type", "access"),
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
    Verify user's email address with verification code
    """
    try:
        result = await auth_service.verify_email(request.code)
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

@router.post("/resend-verification", response_model=dict)
async def resend_verification_code(
    request: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Resend verification code to user's email
    """
    try:
        result = await auth_service.resend_verification_code(request.email)
        logger.info(f"Verification code resent to: {request.email}")
        return result
    except ValueError as e:
        logger.warning(f"Resend verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resending verification code: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resend verification service error"
        )

@router.post("/request-password-reset", response_model=dict)
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset by sending reset code to email
    """
    try:
        result = await auth_service.request_password_reset(request.email)
        logger.info(f"Password reset requested for: {request.email}")
        return result
    except Exception as e:
        logger.error(f"Error requesting password reset: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/confirm-password-reset", response_model=dict)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Confirm password reset with code and new password
    """
    try:
        result = await auth_service.confirm_password_reset(request.code, request.new_password)
        logger.info(f"Password reset confirmed for user: {result.get('email')}")
        return {
            "message": "Password reset successfully. You can now log in with your new password.",
            "success": True
        }
    except ValueError as e:
        logger.warning(f"Password reset confirmation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error confirming password reset: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    """
    try:
        tokens = await auth_service.refresh_access_token(request.refresh_token)
        
        # Get user info for the response
        payload = await auth_service.verify_jwt_token(tokens['access_token'])
        if not payload:
            raise ValueError("Failed to verify new access token")
            
        user = await auth_service.user_repository.get_by_id(payload['user_id'])
        if not user:
            raise ValueError("User not found")
        
        return AuthResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type="bearer",
            user_id=str(user.id),
            email=user.email,
            name=user.name,
            is_verified=user.is_verified
        )
    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh service error"
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
                detail="Token expired or invalid. Please refresh your token or login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Ensure it's an access token, not a refresh token
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Please use an access token.",
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

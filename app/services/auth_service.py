"""
Authentication service implementation
"""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from app.models.entities import User
from app.models.dtos import AuthResponse
from app.repositories.user_repository import UserRepository
from app.services.interfaces import AuthServiceInterface
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class AuthService(AuthServiceInterface):
    """Service for handling authentication operations"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.jwt_secret = settings.JWT_SECRET
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwt_expiration = settings.JWT_EXPIRATION_HOURS
    
    async def authenticate_google_token(self, token: str) -> AuthResponse:
        """Authenticate user with Google token"""
        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            # Extract user information
            google_id = idinfo.get('sub')
            email = idinfo.get('email')
            name = idinfo.get('name')
            picture = idinfo.get('picture')
            
            if not google_id or not email:
                raise ValueError("Invalid Google token: missing required fields")
            
            # Check if user exists
            user = await self.user_repository.get_by_google_id(google_id)
            
            if not user:
                # Check if user exists with this email
                user = await self.user_repository.get_by_email(email)
                if user:
                    # Update existing user with Google ID
                    user.google_id = google_id
                    user.name = name or user.name
                    user.picture = picture or user.picture
                    user = await self.user_repository.update_user(user)
                else:
                    # Create new user
                    user_data = {
                        'email': email,
                        'google_id': google_id,
                        'name': name,
                        'picture': picture,
                        'created_at': utc_now(),
                        'updated_at': utc_now(),
                        'is_active': True
                    }
                    user = await self.user_repository.create_user(user_data)
            
            # Generate JWT token
            access_token = await self.create_jwt_token(user)
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=str(user.id),
                email=user.email,
                name=user.name
            )
            
        except Exception as e:
            logger.error(f"Error authenticating Google token: {e}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    async def create_jwt_token(self, user: User) -> str:
        """Create JWT token for user"""
        try:
            payload = {
                'user_id': str(user.id),
                'email': user.email,
                'exp': utc_now() + timedelta(hours=self.jwt_expiration),
                'iat': utc_now()
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error creating JWT token for user {user.id}: {e}")
            raise
    
    async def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

"""
Authentication service implementation
"""
import jwt
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from app.models.entities import User
from app.models.dtos import AuthResponse
from app.repositories.user_repository import UserRepository
from app.services.interfaces import AuthServiceInterface
from app.services.email_service import EmailService
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class AuthService(AuthServiceInterface):
    """Service for handling authentication operations"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.email_service = EmailService()
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
                name=user.name,
                is_verified=True  # Google users are automatically verified
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
    
    async def register_with_email(self, email: str, username: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Register user with email and username"""
        try:
            # Check if email already exists
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError("Email already registered")
            
            # Check if username already exists
            existing_username = await self.user_repository.get_by_username(username)
            if existing_username:
                raise ValueError("Username already taken")
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Create user data
            user_data = {
                'email': email,
                'username': username,
                'password_hash': password_hash,
                'verification_token': verification_token,
                'name': name,
                'is_verified': False,
                'is_active': True,
                'created_at': utc_now(),
                'updated_at': utc_now()
            }
            
            # Create user
            user = await self.user_repository.create_user(user_data)
            
            # Send verification email
            email_sent = await self.email_service.send_verification_email(email, verification_token)
            if not email_sent:
                logger.warning(f"Failed to send verification email to {email}")
            
            return {
                'user_id': str(user.id),
                'email': user.email
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error registering user with email {email}: {e}")
            raise ValueError("Registration failed")
    
    async def authenticate_email_login(self, email_or_username: str, password: str) -> AuthResponse:
        """Authenticate user with email/username and password"""
        try:
            # Find user by email or username
            user = await self.user_repository.get_by_email(email_or_username)
            if not user:
                user = await self.user_repository.get_by_username(email_or_username)
            
            if not user:
                raise ValueError("Invalid credentials")
            
            # Check if user registered with email (has password)
            if not user.password_hash:
                raise ValueError("Please use Google login for this account")
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                raise ValueError("Invalid credentials")
            
            # Check if email is verified
            if not user.is_verified:
                raise ValueError("Please verify your email before logging in")
            
            # Check if account is active
            if not user.is_active:
                raise ValueError("Account is deactivated")
            
            # Generate JWT token
            access_token = await self.create_jwt_token(user)
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                is_verified=user.is_verified
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error authenticating email login for {email_or_username}: {e}")
            raise ValueError("Authentication failed")
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user's email with verification token"""
        try:
            # Find user by verification token
            user = await self.user_repository.get_by_verification_token(token)
            if not user:
                raise ValueError("Invalid or expired verification token")
            
            # Check if already verified
            if user.is_verified:
                raise ValueError("Email already verified")
            
            # Update user as verified
            user.is_verified = True
            user.verification_token = None  # Clear the token
            user.updated_at = utc_now()
            
            await self.user_repository.update_user(user)
            
            return {
                'email': user.email,
                'verified': True
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error verifying email with token: {e}")
            raise ValueError("Email verification failed")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return stored_hash == password_hash_check.hex()
        except Exception:
            return False

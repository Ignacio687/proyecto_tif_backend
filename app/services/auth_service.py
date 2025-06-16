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
            
            # Generate short verification code (6 alphanumeric characters)
            verification_code = self._generate_verification_code()
            verification_code_expires = utc_now() + timedelta(minutes=30)
            
            # Create user data
            user_data = {
                'email': email,
                'username': username,
                'password_hash': password_hash,
                'verification_code': verification_code,
                'verification_code_expires': verification_code_expires,
                'name': name,
                'is_verified': False,
                'is_active': True,
                'created_at': utc_now(),
                'updated_at': utc_now()
            }
            
            # Create user
            user = await self.user_repository.create_user(user_data)
            
            # Send verification email
            email_sent = await self.email_service.send_verification_email(email, verification_code)
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
    
    async def verify_email(self, code: str) -> Dict[str, Any]:
        """Verify user's email with verification code"""
        try:
            # Find user by verification code
            user = await self.user_repository.get_by_verification_code(code)
            if not user:
                raise ValueError("Invalid or expired verification code")
            
            # Check if code has expired
            if user.verification_code_expires:
                # Ensure both datetimes are timezone-aware for comparison
                expires_at = user.verification_code_expires
                if expires_at.tzinfo is None:
                    # If the stored datetime is naive, assume it's UTC
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at < utc_now():
                    raise ValueError("Verification code has expired")
            
            # Check if already verified
            if user.is_verified:
                raise ValueError("Email already verified")
            
            # Update user as verified
            user.is_verified = True
            user.verification_code = None  # Clear the code
            user.verification_code_expires = None
            user.updated_at = utc_now()
            
            await self.user_repository.update_user(user)
            
            return {
                'email': user.email,
                'verified': True
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error verifying email with code: {e}")
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
    
    def _generate_verification_code(self) -> str:
        """Generate a 6-character alphanumeric verification code"""
        return secrets.token_hex(3).upper()  # 6 characters: 0-9 and A-F
    
    def _generate_reset_code(self) -> str:
        """Generate a 6-character alphanumeric reset code"""
        return secrets.token_hex(3).upper()  # 6 characters: 0-9 and A-F

    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset for user"""
        try:
            # Find user by email
            user = await self.user_repository.get_by_email(email)
            if not user:
                # Don't reveal if email exists or not for security
                return {"message": "If this email is registered, you will receive a reset code"}
            
            # Check if user has password (not Google-only account)
            if not user.password_hash:
                return {"message": "This account uses Google login. Please use Google to sign in"}
            
            # Generate reset code
            reset_code = self._generate_reset_code()
            reset_code_expires = utc_now() + timedelta(minutes=30)
            
            # Update user with reset code
            user.reset_code = reset_code
            user.reset_code_expires = reset_code_expires
            user.updated_at = utc_now()
            
            await self.user_repository.update_user(user)
            
            # Send reset email
            email_sent = await self.email_service.send_password_reset_email(email, reset_code)
            if not email_sent:
                logger.warning(f"Failed to send password reset email to {email}")
            
            return {"message": "If this email is registered, you will receive a reset code"}
            
        except Exception as e:
            logger.error(f"Error requesting password reset for {email}: {e}")
            return {"message": "If this email is registered, you will receive a reset code"}
    
    async def confirm_password_reset(self, code: str, new_password: str) -> Dict[str, Any]:
        """Confirm password reset with code and new password"""
        try:
            # Find user by reset code
            user = await self.user_repository.get_by_reset_code(code)
            if not user:
                raise ValueError("Invalid or expired reset code")
            
            # Check if code has expired
            if user.reset_code_expires:
                # Ensure both datetimes are timezone-aware for comparison
                expires_at = user.reset_code_expires
                if expires_at.tzinfo is None:
                    # If the stored datetime is naive, assume it's UTC
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at < utc_now():
                    raise ValueError("Reset code has expired")
            
            # Hash new password
            new_password_hash = self._hash_password(new_password)
            
            # Update user password and clear reset code
            user.password_hash = new_password_hash
            user.reset_code = None
            user.reset_code_expires = None
            user.updated_at = utc_now()
            
            await self.user_repository.update_user(user)
            
            return {
                'email': user.email,
                'message': 'Password reset successfully'
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error confirming password reset: {e}")
            raise ValueError("Password reset failed")

    async def resend_verification_code(self, email: str) -> Dict[str, Any]:
        """Resend verification code to user email"""
        try:
            # Find user by email
            user = await self.user_repository.get_by_email(email)
            if not user:
                return {"message": "If this email is registered, a new verification code will be sent"}
            
            # Check if already verified
            if user.is_verified:
                raise ValueError("Email is already verified")
            
            # Generate new verification code
            verification_code = self._generate_verification_code()
            verification_code_expires = utc_now() + timedelta(minutes=30)
            
            # Update user with new code
            user.verification_code = verification_code
            user.verification_code_expires = verification_code_expires
            user.updated_at = utc_now()
            
            await self.user_repository.update_user(user)
            
            # Send verification email
            email_sent = await self.email_service.send_verification_email(email, verification_code)
            if not email_sent:
                logger.warning(f"Failed to resend verification email to {email}")
            
            return {"message": "A new verification code has been sent to your email"}
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error resending verification code for {email}: {e}")
            return {"message": "If this email is registered, a new verification code will be sent"}

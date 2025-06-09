"""
User repository implementation using Beanie ODM
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.models.entities import User
from app.repositories.interfaces import UserRepositoryInterface
from app.logger import logger


def utc_now() -> datetime:
    """Get current UTC datetime with timezone awareness"""
    return datetime.now(timezone.utc)


class UserRepository(UserRepositoryInterface):
    """Repository for user operations"""
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        try:
            return await User.find_one(User.google_id == google_id)
        except Exception as e:
            logger.error(f"Error getting user by Google ID {google_id}: {e}")
            return None
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        try:
            user = User(**user_data)
            await user.create()
            logger.info(f"Created new user: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def update_user(self, user: User) -> User:
        """Update an existing user"""
        try:
            user.updated_at = utc_now()
            await user.save()
            logger.info(f"Updated user: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error updating user {user.id}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return await User.find_one(User.username == username)
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token"""
        try:
            return await User.find_one(User.verification_token == token)
        except Exception as e:
            logger.error(f"Error getting user by verification token: {e}")
            return None

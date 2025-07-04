"""
Dependency injection container for the application
"""
from app.services.auth_service import AuthService
from app.services.assistant_service import AssistantService
from app.services.gemini_service import GeminiService
from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.key_context_repository import KeyContextRepository


class DependencyContainer:
    """Container for managing application dependencies with proper singleton behavior"""
    
    def __init__(self):
        # Repositories - shared instances to reuse database connections
        self._user_repository = None
        self._conversation_repository = None
        self._context_repository = None
        
        # Services - inject repositories to avoid creating new database connections
        self._auth_service = None
        self._assistant_service = None
        self._gemini_service = None
    
    @property
    def user_repository(self) -> UserRepository:
        """Get singleton UserRepository instance"""
        if self._user_repository is None:
            self._user_repository = UserRepository()
        return self._user_repository
    
    @property
    def conversation_repository(self) -> ConversationRepository:
        """Get singleton ConversationRepository instance"""
        if self._conversation_repository is None:
            self._conversation_repository = ConversationRepository()
        return self._conversation_repository
    
    @property
    def context_repository(self) -> KeyContextRepository:
        """Get singleton KeyContextRepository instance"""
        if self._context_repository is None:
            self._context_repository = KeyContextRepository()
        return self._context_repository
    
    @property
    def auth_service(self) -> AuthService:
        """Get singleton AuthService instance with injected dependencies"""
        if self._auth_service is None:
            # Inject repositories as dependencies to ensure reuse of connections
            self._auth_service = AuthService(
                user_repository=self.user_repository,
                email_service=None,  # EmailService doesn't use database connections
                key_context_repository=self.context_repository
            )
        return self._auth_service
    
    @property
    def assistant_service(self) -> AssistantService:
        """Get singleton AssistantService instance with injected dependencies"""
        if self._assistant_service is None:
            # Inject repositories as dependencies to ensure reuse of connections
            self._assistant_service = AssistantService(
                conversation_repository=self.conversation_repository,
                key_context_repository=self.context_repository,
                gemini_service=self.gemini_service
            )
        return self._assistant_service
    
    @property
    def gemini_service(self) -> GeminiService:
        """Get singleton GeminiService instance"""
        if self._gemini_service is None:
            self._gemini_service = GeminiService()      
        return self._gemini_service


# Global dependency container - this ensures all services share the same repository instances
container = DependencyContainer()


# Dependency functions for FastAPI
def get_auth_service() -> AuthService:
    """Get AuthService instance from container"""
    return container.auth_service


def get_assistant_service() -> AssistantService:
    """Get AssistantService instance from container"""
    return container.assistant_service


def get_user_repository() -> UserRepository:
    """Get UserRepository instance from container"""
    return container.user_repository


def get_conversation_repository() -> ConversationRepository:
    """Get ConversationRepository instance from container"""
    return container.conversation_repository


def get_context_repository() -> KeyContextRepository:
    """Get KeyContextRepository instance from container"""
    return container.context_repository

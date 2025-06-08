"""
Dependency injection container for the application
"""
from app.services.auth_service import AuthService
from app.services.assistant_service import AssistantService
from app.services.gemini_service import GeminiService
from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.summarized_context_repository import SummarizedContextRepository


class DependencyContainer:
    """Container for managing application dependencies"""
    
    def __init__(self):
        # Repositories
        self._user_repository = None
        self._conversation_repository = None
        self._context_repository = None
        
        # Services
        self._auth_service = None
        self._assistant_service = None
        self._gemini_service = None
    
    @property
    def user_repository(self) -> UserRepository:
        if self._user_repository is None:
            self._user_repository = UserRepository()
        return self._user_repository
    
    @property
    def conversation_repository(self) -> ConversationRepository:
        if self._conversation_repository is None:
            self._conversation_repository = ConversationRepository()
        return self._conversation_repository
    
    @property
    def context_repository(self) -> SummarizedContextRepository:
        if self._context_repository is None:
            self._context_repository = SummarizedContextRepository()
        return self._context_repository
    
    @property
    def auth_service(self) -> AuthService:
        if self._auth_service is None:
            self._auth_service = AuthService()
        return self._auth_service
    
    @property
    def assistant_service(self) -> AssistantService:
        if self._assistant_service is None:
            self._assistant_service = AssistantService()
        return self._assistant_service
    
    @property
    def gemini_service(self) -> GeminiService:
        if self._gemini_service is None:
            self._gemini_service = GeminiService()      
        return self._gemini_service


# Global dependency container
container = DependencyContainer()


# Dependency functions for FastAPI
def get_auth_service() -> AuthService:
    return container.auth_service


def get_assistant_service() -> AssistantService:
    return container.assistant_service


def get_user_repository() -> UserRepository:
    return container.user_repository


def get_conversation_repository() -> ConversationRepository:
    return container.conversation_repository


def get_context_repository() -> SummarizedContextRepository:
    return container.context_repository

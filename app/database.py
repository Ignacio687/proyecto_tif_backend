"""
Database initialization and configuration
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.entities import User, Conversation, KeyContext
from app.logger import logger


class DatabaseManager:
    """Manages database connection and initialization"""
    
    def __init__(self):
        self.client = None
        self.database = None
    
    async def initialize_database(self):
        """Initialize database connection and Beanie ODM"""
        try:
            # Create MongoDB client
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.database = self.client[settings.MONGODB_DB]
            
            # Initialize Beanie with all document models
            await init_beanie(
                database=self.database,
                document_models=[User, Conversation, KeyContext]
            )
            
            logger.info(f"Database connection established to {settings.MONGODB_DB}")
            logger.info("All document models initialized with Beanie ODM")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close_database(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Global database manager instance
db_manager = DatabaseManager()

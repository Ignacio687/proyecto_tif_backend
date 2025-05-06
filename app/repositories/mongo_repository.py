from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]

    # Basic CRUD methods (placeholder)
    # async def insert_data(self, data):
    #     pass

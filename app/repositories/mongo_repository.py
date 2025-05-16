from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime
from app.models.request_response import Conversation

class MongoRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db["conversations"]

    async def save_conversation(self, user_input: str, server_reply: str):
        conversation = {
            "user_input": user_input,
            "server_reply": server_reply,
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(conversation)

    async def get_last_conversations(self, limit: int = 25):
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

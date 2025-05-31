from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime
from app.models.request_response import Conversation
from app.logger import logger

class MongoRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db["conversations"]

    async def save_conversation(self, user_input: str, server_reply: str, interaction_params: dict | None = None):
        conversation = {
            "user_input": user_input,
            "server_reply": server_reply,
            "timestamp": datetime.utcnow()
        }
        if interaction_params is not None:
            conversation["interaction_params"] = interaction_params
        await self.collection.insert_one(conversation)

    async def get_last_conversations(self, limit: int = 4):
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def save_summarized_context(self, summarized_context):
        """
        Save the summarized context to the database (summarized_context collection).
        """
        await self.db["summarized_context"].replace_one(
            {},  # Only one document
            {"interactions": summarized_context},
            upsert=True
        )

    async def get_summarized_context(self):
        """
        Load the summarized context from the database (summarized_context collection).
        """
        doc = await self.db["summarized_context"].find_one({})
        logger.debug(f"[MongoRepository] Raw summarized_context doc from DB: {doc}")
        if doc and "interactions" in doc:
            return doc["interactions"]
        return []

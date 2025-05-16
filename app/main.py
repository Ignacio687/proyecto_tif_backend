from fastapi import FastAPI
from app.api.v1.controllers import router as v1_router
from app.logger import logger
from contextlib import asynccontextmanager
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TIF Backend API...")
    # Initialize Beanie
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(database=client['tif_db'], document_models=[User])
    yield
    logger.info("Shutting down TIF Backend API...")

app = FastAPI(title="TIF Backend API", version="1.0.0", lifespan=lifespan)

app.include_router(v1_router, prefix="/api/v1")

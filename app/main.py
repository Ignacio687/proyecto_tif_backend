from fastapi import FastAPI
from app.api.assistant_controller import router as assistant_router
from app.api.auth_controller import router as auth_router
from app.logger import logger
from app.database import db_manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TIF Backend API...")
    # Initialize database
    await db_manager.initialize_database()
    yield
    # Close database connection
    await db_manager.close_database()
    logger.info("Shutting down TIF Backend API...")

app = FastAPI(title="TIF Backend API", version="1.0.0", lifespan=lifespan)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(assistant_router, prefix="/api/v1", tags=["assistant"])

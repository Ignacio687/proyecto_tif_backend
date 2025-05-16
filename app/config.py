import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.environ.get("MONGODB_DB", "AI_Assistant_db")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

settings = Settings()

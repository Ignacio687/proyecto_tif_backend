import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database settings
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.environ.get("MONGODB_DB", "tif_db")
    
    # AI Service settings
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    
    # Authentication settings
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    
    # Email settings
    SMTP_SERVER: str = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.environ.get("FROM_EMAIL", "")
    
    # Application settings
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"

settings = Settings()

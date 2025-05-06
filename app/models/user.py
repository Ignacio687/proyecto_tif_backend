from beanie import Document
from pydantic import Field

class User(Document):
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")

    class Settings:
        name = "users"

from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr
from datetime import datetime # Add this import

class User(Document):
    username: str
    email: Indexed(str, unique=True)
    hashed_password: str
    is_verified: bool = False
    verification_code: Optional[str] = None
    code_expires_at: Optional[datetime] = None  # New field for expiration

    class Settings:
        name = "users"  # The collection name in MongoDB

# This is used for the registration request validation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
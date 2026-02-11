from beanie import Document
from pydantic import BaseModel, EmailStr

# 1. This is what the user sends in the JSON body
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # The plain text password from the curl

# 2. This is what actually stays in MongoDB
class User(Document):
    username: str
    email: EmailStr
    hashed_password: str

    class Settings:
        name = "users"
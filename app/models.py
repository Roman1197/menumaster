from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr

# --- Menu Related Models ---

class MenuItem(BaseModel):
    """Represents a single dish in the menu"""
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    image_url: Optional[str] = None

class MenuCategory(BaseModel):
    """Represents a category like 'Starters' or 'Main Courses'"""
    name: str
    items: List[MenuItem] = []

class Menu(Document):
    """The main Menu document stored in MongoDB"""
    title: str
    owner_id: str  # References the User.id (as a string) who created this menu
    categories: List[MenuCategory] = []
    is_active: bool = True

    class Settings:
        name = "menus"  # Collection name in MongoDB

# --- User Related Models ---

class User(Document):
    """The User document stored in MongoDB with auth and verification fields"""
    username: str
    email: Indexed(str, unique=True)
    hashed_password: str
    is_verified: bool = False
    verification_code: Optional[str] = None
    code_expires_at: Optional[datetime] = None

    class Settings:
        name = "users"  # Collection name in MongoDB

class UserCreate(BaseModel):
    """Schema for validating user registration requests"""
    username: str
    email: EmailStr
    password: str
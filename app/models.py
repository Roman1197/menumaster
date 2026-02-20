from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr
from enum import Enum

# 1. Roles (חייב להיות ראשון)
class UserRole(str, Enum):
    """Defined roles for Role-Based Access Control (RBAC)"""
    RESTAURANT_OWNER = "owner"
    REGULAR_USER = "customer"

# 2. Restaurant Model (העברתי לפה כדי שיהיה מוגדר לפני ה-Menu)
class Restaurant(Document):
    """The Restaurant entity owned by a user"""
    name: Indexed(str)
    location: str
    image_url: Optional[str] = None
    owner_id: str  # References User.id
    menu_ids: List[str] = [] 
    is_active: bool = True

    class Settings:
        name = "restaurants"

# 3. Menu Related Models
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
    restaurant_id: str # Linked to Restaurant
    owner_id: str  # References the User.id
    categories: List[MenuCategory] = []
    is_active: bool = False

    class Settings:
        name = "menus"

# 4. User Models
class User(Document):
    """The User document stored in MongoDB"""
    username: Indexed(str, unique=True) 
    email: Indexed(str, unique=True)
    hashed_password: str
    is_verified: bool = False
    verification_code: Optional[str] = None
    role: UserRole = UserRole.REGULAR_USER
    code_expires_at: Optional[datetime] = None

    class Settings:
        name = "users"

class UserCreate(BaseModel):
    """Schema for validating user registration requests"""
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.REGULAR_USER
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt  # PyJWT

from app.models import User, UserCreate

router = APIRouter()

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token valid for 24 hours

# Pydantic models for requests and responses
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str

# Helper function to generate JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    # Check if user already exists in MongoDB
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already exists"
        )
    
    # Encrypt the password
    hashed = pwd_context.hash(user_in.password)
    
    # Create the Beanie document
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed
    )
    
    await new_user.insert()
    return {"message": "Registration successful", "id": str(new_user.id)}

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    # 1. Search for the user by email
    user = await User.find_one(User.email == credentials.email)
    
    # 2. Validate existence and password
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create the JWT (Payload contains user ID and email)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }
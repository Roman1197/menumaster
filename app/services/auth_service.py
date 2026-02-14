import os
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from fastapi import HTTPException, status
from app.models import User, UserCreate

class AuthService:
    # Security configurations
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
    CODE_EXPIRATION_MINUTES = 10  # Code expires after 10 minutes

    @classmethod
    async def register_user(cls, user_in: UserCreate):
        # 1. Check if user already exists
        existing_user = await User.find_one(User.email == user_in.email)
        if existing_user:
            return None
        
        # 2. Hash password - Make sure the variable name matches!
        hashed = cls.pwd_context.hash(user_in.password)
        
        # 3. Generate initial verification code and expiry
        initial_code = ''.join(random.choices(string.digits, k=6))
        expiry_time = datetime.utcnow() + timedelta(minutes=cls.CODE_EXPIRATION_MINUTES)
        
        # 4. Create new user document
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed, # Fixed: using 'hashed' variable
            is_verified=False,
            verification_code=initial_code,
            code_expires_at=expiry_time
        )
        
        # 5. Insert to MongoDB
        await new_user.insert()
        
        # Debug print
        print(f"DEBUG: User registered: {new_user.email} with code: {initial_code}")
        
        return new_user

    @classmethod
    async def authenticate_user(cls, email: str, password: str):
        user = await User.find_one(User.email == email)
        if not user or not cls.pwd_context.verify(password, user.hashed_password):
            return None
        return user

    @classmethod
    def create_access_token(cls, user: User):
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "exp": expire,
            "sub": str(user.id),
            "email": user.email
        }
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    async def verify_email_code(cls, email: str, code: str):
        user = await User.find_one(User.email == email)
        
        if not user or user.verification_code != code:
            return "INVALID"
        
        # Check if code has expired
        if datetime.utcnow() > user.code_expires_at:
            return "EXPIRED"
            
        user.is_verified = True
        user.verification_code = None
        user.code_expires_at = None
        await user.save()
        return "SUCCESS"

    @classmethod
    async def resend_verification_code(cls, email: str):
        user = await User.find_one(User.email == email)
        if not user:
            return None
        if user.is_verified:
            return "ALREADY_VERIFIED"
            
        # Generate new code and new expiration
        new_code = ''.join(random.choices(string.digits, k=6))
        expiry_time = datetime.utcnow() + timedelta(minutes=cls.CODE_EXPIRATION_MINUTES)
        
        user.verification_code = new_code
        user.code_expires_at = expiry_time
        await user.save()
        
        print(f"DEBUG: Resent code for {email}: {new_code}")
        return True
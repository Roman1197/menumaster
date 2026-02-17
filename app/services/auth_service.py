import os
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from fastapi import HTTPException, status

# Imports from my project
from app.models import User, UserCreate
from app.services.email_service import EmailService

class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
    CODE_EXPIRATION_MINUTES = 10

    @classmethod
    async def register_user(cls, user_in: UserCreate):
        existing_user = await User.find_one(User.email == user_in.email)
        if existing_user:
            return None
        
        hashed = cls.pwd_context.hash(user_in.password)
        initial_code = ''.join(random.choices(string.digits, k=6))
        expiry_time = datetime.utcnow() + timedelta(minutes=cls.CODE_EXPIRATION_MINUTES)
        
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed,
            is_verified=False,
            verification_code=initial_code,
            code_expires_at=expiry_time
        )
        
        await new_user.insert()
        
        # --- SEND REAL EMAIL ---
        await EmailService.send_verification_email(new_user.email, initial_code)
        
        return new_user

    @classmethod
    async def authenticate_user(cls, email: str, password: str):
        user = await User.find_one(User.email == email)
        if not user or not cls.pwd_context.verify(password, user.hashed_password):
            return None
        
        # Prevent login if not verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in."
            )
        return user

    @classmethod
    async def verify_email_code(cls, email: str, code: str):
        user = await User.find_one(User.email == email)
        if not user or user.verification_code != code:
            return "INVALID"
        
        if datetime.utcnow() > user.code_expires_at:
            return "EXPIRED"
            
        user.is_verified = True
        user.verification_code = None
        user.code_expires_at = None
        await user.save()

        # --- שליחת מייל ברוכים הבאים לאחר אימות מוצלח ---
        await EmailService.send_welcome_email(user.email, user.username)
        
        return "SUCCESS"

    @classmethod
    async def resend_verification_code(cls, email: str):
        user = await User.find_one(User.email == email)
        if not user:
            return None
        if user.is_verified:
            return "ALREADY_VERIFIED"
            
        new_code = ''.join(random.choices(string.digits, k=6))
        expiry_time = datetime.utcnow() + timedelta(minutes=cls.CODE_EXPIRATION_MINUTES)
        
        user.verification_code = new_code
        user.code_expires_at = expiry_time
        await user.save()
        
        # --- SEND REAL EMAIL ---
        await EmailService.send_verification_email(user.email, new_code)
        return True

    @classmethod
    def create_access_token(cls, user: User):
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expire, "sub": str(user.id), "email": user.email}
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    async def get_current_user(cls, token: str):
        """
        Decodes the JWT token and returns the user from the database.
        Checks if the user exists and is verified.
        """
        try:
            # Decode the JWT token
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        # Fetch the user from MongoDB
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Hard enforcement: User must be verified to perform business actions
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
            
        return user
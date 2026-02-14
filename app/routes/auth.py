from fastapi import APIRouter, HTTPException, status
from app.models import UserCreate
from app.services.auth_service import AuthService
from pydantic import BaseModel, EmailStr

router = APIRouter()

# --- Request Models ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

class ResendCodeRequest(BaseModel):
    email: EmailStr

# --- Routes ---

@router.post("/register", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_in: UserCreate):
    # Registration logic including initial code generation
    user = await AuthService.register_user(user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already exists"
        )
    return {"message": "Registration successful. Please check your email for the verification code.", "id": str(user.id)}

@router.post("/login", tags=["Authentication"])
async def login(credentials: LoginRequest):
    # Business logic moved to AuthService
    user = await AuthService.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate JWT for authenticated user
    token = AuthService.create_access_token(user)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username
    }

@router.post("/verify-email", tags=["Authentication"])
async def verify_email(data: VerifyRequest):
    # Verify the 6-digit code and check expiration
    result = await AuthService.verify_email_code(data.email, data.code)
    
    if result == "INVALID":
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    if result == "EXPIRED":
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")
        
    return {"message": "Email verified successfully"}

@router.post("/resend-code", tags=["Authentication"])
async def resend_code(data: ResendCodeRequest):
    # Generate a new code and update the expiration time
    result = await AuthService.resend_verification_code(data.email)
    
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    if result == "ALREADY_VERIFIED":
        return {"message": "Account is already verified. You can log in."}
        
    return {"message": "A new verification code has been generated and sent."}
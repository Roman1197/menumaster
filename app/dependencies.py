# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService

# This triggers the "Authorize" button in Swagger UI
security = HTTPBearer()

async def get_verified_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency that ensures the request has a valid JWT 
    and the user is email-verified.
    """
    return await AuthService.get_current_user(auth.credentials)
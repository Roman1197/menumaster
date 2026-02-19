from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.models import User, UserRole

# This triggers the "Authorize" button in Swagger UI
security = HTTPBearer()

async def get_verified_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency that ensures the request has a valid JWT 
    and the user is email-verified.
    """
    return await AuthService.get_current_user(auth.credentials)

async def get_restaurant_owner(current_user: User = Depends(get_verified_user)) -> User:
    """
    Dependency to ensure the user has 'owner' privileges.
    Used for routes that modify menu data (RBAC).
    """
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This action requires a Restaurant Owner account."
        )
    return current_user
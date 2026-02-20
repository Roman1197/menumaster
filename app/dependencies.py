from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.models import User, UserRole
from app.logger import logger  # ייבוא הלוגר לתיעוד אירועי אבטחה

# הגדרת ה-Bearer Token עבור Swagger והקליינט
security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    שכבה 1: אימות בסיסי.
    בודק שהטוקן תקין ומחזיר את המשתמש.
    """
    user = await AuthService.get_current_user(auth.credentials)
    if not user:
        logger.warning("Failed login attempt: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    שכבה 2: אימות אימייל.
    מוודא שהמשתמש אימת את החשבון שלו (is_verified).
    """
    if not current_user.is_verified:
        logger.warning(f"Access denied: User {current_user.email} is not verified")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address to perform this action."
        )
    return current_user

async def get_restaurant_owner(current_user: User = Depends(get_verified_user)) -> User:
    """
    שכבה 3: הרשאות (RBAC).
    מוודא שהמשתמש הוא גם מאומת וגם בעל תפקיד 'owner'.
    """
    if current_user.role != UserRole.RESTAURANT_OWNER:
        logger.warning(f"Unauthorized access attempt: User {current_user.email} (Role: {current_user.role}) tried to access owner route")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This action requires a Restaurant Owner account."
        )
    return current_user
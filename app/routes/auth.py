from fastapi import APIRouter, HTTPException
from app.models import User, UserCreate  # Import both
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(user_in: UserCreate): # Change type to UserCreate
    # Check if user exists
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash the password from the input
    hashed = pwd_context.hash(user_in.password)
    
    # Create the Beanie document
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed
    )
    
    await new_user.insert()
    return {"message": "Registration successful", "id": str(new_user.id)}
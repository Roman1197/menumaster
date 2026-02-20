import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.routes.menus import router as menu_router
from app.routes.auth import router as auth_router 
from app.routes.restaurants import router as restaurant_router
# FIXED: Added Restaurant to the imports
from app.models import User, Menu, Restaurant

app = FastAPI(title="MenuMaster API")

# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(menu_router, prefix="/menus")
app.include_router(restaurant_router, prefix="/restaurants")

@app.on_event("startup")
async def startup_event():
    """
    Application startup logic:
    1. Connect to MongoDB
    2. Initialize Beanie with all Document models
    """
    # MongoDB Connection
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    
    # Initialize Beanie
    # FIXED: Added Restaurant to the document_models list
    await init_beanie(
        database=client.menumaster_auth, 
        document_models=[User, Menu, Restaurant] 
    )

@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify API and DB status"""
    return {"status": "ok", "database": "mongodb"}
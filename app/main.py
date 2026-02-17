import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.routes.menus import router as menu_router
from app.routes.auth import router as auth_router 
from app.models import User, Menu

app = FastAPI(title="MenuMaster API")

# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(menu_router, prefix="/menus")

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
    # Added 'Menu' to the document_models list to fix CollectionWasNotInitialized error
    await init_beanie(
        database=client.menumaster_auth, 
        document_models=[User, Menu] 
    )

@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify API and DB status"""
    return {"status": "ok", "database": "mongodb"}
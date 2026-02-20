import os
import uuid
from app.logger import logger, request_id_contextvar 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Imports of routers and models
from app.routes.menus import router as menu_router
from app.routes.auth import router as auth_router 
from app.routes.restaurants import router as restaurant_router
from app.models import User, Menu, Restaurant

app = FastAPI(title="MenuMaster API")

# --- הגדרות CORS ---
# שיניתי מעט את ההגדרות כדי לוודא שדפדפנים (Flutter Web) מקבלים אישור מלא
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בפיתוח נאפשר הכל. בייצור נחליף לכתובת הקליינט.
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(menu_router, prefix="/menus")
app.include_router(restaurant_router, prefix="/restaurants", tags=["Restaurants"])
@app.on_event("startup")
async def startup_event():
    """
    מנהל את החיבור למונגו ואינטראקציה עם Beanie
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in environment variables")

    client = AsyncIOMotorClient(database_url)
    
    # אתחול Beanie עם כל המודלים
    # ודאנו ש-Restaurant מופיע כאן כדי למנוע CollectionWasNotInitialized
    await init_beanie(
        database=client.menumaster_auth, 
        document_models=[User, Menu, Restaurant] 
    )

@app.get("/health")
async def health_check():
    """בדיקת תקינות מהירה של השרת"""
    return {"status": "ok", "database": "mongodb"}
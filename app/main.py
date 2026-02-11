import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Ensure these paths match your folder structure!
from app.models import User
from app.routes.auth import router as auth_router 

app = FastAPI(title="MenuMaster API")

# This is the line that makes the routes appear in Swagger
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.on_event("startup")
async def startup_event():
    # MongoDB Connection
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    # Initialize Beanie with your MongoDB models
    await init_beanie(database=client.menumaster_auth, document_models=[User])

@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "mongodb"}




from fastapi import FastAPI
import cloudinary
from fastapi.middleware.cors import CORSMiddleware

from app.api import items, auth
from app.core.config import settings
from database.connection import engine, Base
from app.models import models


Base.metadata.create_all(bind=engine)

cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME, 
    api_key = settings.CLOUDINARY_API_KEY, 
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure = True
)

app = FastAPI(
    title="lost&found",
    description="Backend for college lost and found system",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"]
    
)

@app.get("/")
def root():
    return{
        "status": "online",
        "docs": "/docs"
    }
    
app.include_router(items.router)
app.include_router(auth.router)


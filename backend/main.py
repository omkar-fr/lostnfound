from fastapi import FastAPI
from database.connection import engine, Base
from app.models import models


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lost~n~Found",
    description="Backend for college lost and found system",
    version="1.0"
)

@app.get("/")
def root():
    return{
        "status": "online",
        "docs": "/docs"
    }
    

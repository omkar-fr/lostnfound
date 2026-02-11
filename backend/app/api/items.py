from datetime import datetime
from typing import Optional
import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import UUID
from sqlalchemy.orm import Session
import cloudinary.uploader

from database.connection import SessionLocal, get_db
from app.models.models import Item
from app.models.schemas import ItemCreate

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/")
def list_items(
    item_type: Optional[str] = None, 
    category: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Item).filter(Item.status == "available")
    
    if item_type:
        query = query.filter(Item.item_type == item_type)
    if category:
        query = query.filter(Item.category == category)
        
    return query.all()

@router.get("/my-items")
def get_my_items(db: Session = Depends(get_db)):
    current_user_id = uuid.UUID("66ecddca-0883-4bdb-aa6f-9ddb259d382b")
    
    items = db.query(Item).filter(Item.user_id == current_user_id).all()
    return items

@router.get("/{item_id}")
def get_item_detail(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/")
async def create_item(
    background_tasks: BackgroundTasks, 
    item_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    event_date: str = Form(...), 
    file: Optional[UploadFile] = File(None),
    ):
    
    if item_type == "found" and not file:
        raise HTTPException(
            status_code=400, 
            detail="Image is mandatory when reporting a found item."
        )

    
    image_url = None
    if file:
        loop = asyncio.get_event_loop()
        try:
            upload_result = await loop.run_in_executor(
                None, lambda: cloudinary.uploader.upload(file.file)
            )
            image_url=upload_result.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    db=SessionLocal()
    try:
        db_item = Item(
            id=uuid.uuid4(),
            item_type=item_type,
            title=title,
            description=description,
            category=category,
            location=location,
            event_date=datetime.fromisoformat(event_date),
            image_url=image_url,
            user_id=uuid.UUID("66ecddca-0883-4bdb-aa6f-9ddb259d382b"), #placeholder for test user 
            created_at=datetime.utcnow())
        db.add(db_item)
        db.commit()
        
        
        return{
            "message": "Item reported successfully!", 
            "item_id": db_item.id,
            "time": db_item.event_date
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
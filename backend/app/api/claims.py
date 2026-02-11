from fastapi import FastAPI, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from database.connection import SessionLocal, get_db
from app.models.models import Claim, Item
from app.models.schemas import ClaimCreate

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("/")
async def create_claim(claim_data: ClaimCreate):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == claim_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        current_user_id = uuid.UUID("66ecddca-0883-4bdb-aa6f-9ddb259d382b")
        
        if item.user_id == current_user_id:
            raise HTTPException(status_code=400, detail="You cannot claim your own item")
        
        new_claim = Claim(
            id=uuid.uuid4(),
            item_id=claim_data.item_id,
            user_id=current_user_id,
            description=claim_data.description,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.add(new_claim)
        db.commit()
        db.refresh(new_claim)

        return {
            "message": "Claim submitted successfully!",
            "claim_id": new_claim.id,
            "status": new_claim.status
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
        
@router.patch("/{claim_id}/confirm")
async def confirm_transaction(claim_id: uuid.UUID, db: Session = Depends(get_db)):
   
    current_user_id = uuid.UUID("66ecddca-0883-4bdb-aa6f-9ddb259d382b")

    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")
    
    item = db.query(Item).filter(Item.id == claim.item_id).first()

    if item.user_id == current_user_id:
        claim.founder_confirmed = True
    
    elif claim.user_id == current_user_id:
        claim.loser_confirmed = True
    
    else:
        raise HTTPException(status_code=403, detail="You are not part of this transaction")

    if claim.founder_confirmed and claim.loser_confirmed:
        claim.status = "completed"
        item.status = "returned" 
    
    db.commit()
    return {
        "status": claim.status,
        "founder_confirmed": claim.founder_confirmed,
        "loser_confirmed": claim.loser_confirmed
    }
from fastapi.security import OAuth2PasswordBearer
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from database.connection import get_db
from app.models.models import User 
from app.models.schemas import Token, UserLogin, UserRegister, VerifyOTP
from app.core.security import get_password_hash, create_access_token, verify_password
from app.core.redis import redis_client
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth")

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "roll_no": current_user.roll_no
    }

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user_exists = db.query(User).filter(User.email == user_in.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )
        
    otp = generate_otp()
    hashed_password = get_password_hash(user_in.password)
    
    pending_user_data = {
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "roll_no": user_in.roll_no,
        "otp": otp
    }
    
    redis_key = f"reg:{user_in.email}"
    redis_client.setex(
        redis_key, 300, json.dumps(pending_user_data)
    )
    
    background_tasks.add_task(send_otp_email, user_in.email, otp)
    
    return {
        "message": "OTP sent to your college email. It expires in 5 minutes."
    }
    
@router.post("/verify-otp")
async def verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    redis_key = f"reg:{data.email}"
    pending_data_json = redis_client.get(redis_key)
    
    if not pending_data_json:
        raise HTTPException(status_code=400, detail="OTP expired or email not found.")

    pending_user = json.loads(pending_data_json)

    if pending_user["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    existing_user = db.query(User).filter(User.email == pending_user["email"]).first()
    if existing_user:
        redis_client.delete(redis_key)
        raise HTTPException(status_code=400, detail="User already registered.")
    
    new_user = User(
        first_name=pending_user["first_name"],
        last_name=pending_user["last_name"],
        email=pending_user["email"],
        hashed_password=pending_user["hashed_password"],
        roll_no=pending_user["roll_no"],
        is_active=True 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    redis_client.delete(redis_key)
    
    return {"message": "User verified and registered successfully!"}

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If this email is registered, an OTP has been sent."}

    otp = generate_otp()
    redis_client.setex(f"reset:{email}", 300, otp)
    background_tasks.add_task(send_otp_email, email, otp)
    
    return {"message": "Password reset OTP sent."}

@router.post("/reset-password")
async def reset_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    stored_otp = redis_client.get(f"reset:{email}")
    if not stored_otp or stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    user = db.query(User).filter(User.email == email).first()
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    redis_client.delete(f"reset:{email}")
    return {"message": "Password reset successful."}

@router.patch("/profile/update")
async def update_profile(
    first_name: str = None, 
    last_name: str = None, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if first_name: current_user.first_name = first_name
    if last_name: current_user.last_name = last_name
    
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}

@router.delete("/profile/delete")
async def delete_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_active = False
    db.commit()
    return {"message": "Account deactivated."}
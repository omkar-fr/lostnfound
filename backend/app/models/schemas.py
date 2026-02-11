from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional

class ItemCreate(BaseModel):
    item_type: str
    title: str
    description: str
    category: str
    location: str
    event_date: datetime
    image_url: Optional[str] = None
    
class ClaimCreate(BaseModel):
    item_id: UUID
    description: str
    
#auth
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    roll_no: str
    
    @field_validator("email")
    @classmethod
    def validate_college_email(cls, value: str):
        if not value.endswith("@mmcoe.edu.in"):
            raise ValueError("Invalid email.")
        return value

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str | None = None
    
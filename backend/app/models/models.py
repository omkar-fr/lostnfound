import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from database.connection import Base

class User(Base):
    __tablename__="users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    roll_no = Column(String, index=True, nullable=False)
    current_year = Column(String, nullable=False)
    department=Column(String, nullable=False)
    is_admin=Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Item(Base):
    __tablename__="items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    item_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)
    location = Column(String)
    event_date = Column(DateTime)
    image_url = Column(String, nullable=True)
    status = Column(String, default="available")
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Claim(Base):
    __tablename__="claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    description = Column(Text, nullable=False)  
    status = Column(String, default="pending")   
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    target_item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    action = Column(String, nullable=False)  
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
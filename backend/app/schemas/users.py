from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base schema for User"""
    email: EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    timezone: str = "Asia/Kolkata"


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user update"""
    timezone: Optional[str] = None
    email: Optional[EmailStr] = None


# Token Schemas
class Token(BaseModel):
    """Schema for access token response"""
    access: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: int  # user_id
    exp: datetime
    type: str


# Email Verification
class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    token: str


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response"""
    message: str


# Registration Response
class RegisterResponse(BaseModel):
    """Schema for registration response"""
    message: str
    verification_token: str

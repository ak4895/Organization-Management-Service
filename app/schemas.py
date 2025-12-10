from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base schema for Organization"""
    organization_name: str = Field(..., min_length=1, max_length=100)


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    organization_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    organization_id: str
    collection_name: str
    admin_email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrganizationGet(BaseModel):
    """Schema for getting organization by name"""
    organization_name: str


class OrganizationDelete(BaseModel):
    """Schema for deleting organization"""
    organization_name: str


class AdminLoginRequest(BaseModel):
    """Schema for admin login"""
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Schema for admin login response"""
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    organization_id: str
    organization_name: str


class TokenData(BaseModel):
    """Schema for JWT token data"""
    admin_id: Optional[str] = None
    organization_id: Optional[str] = None
    email: Optional[str] = None

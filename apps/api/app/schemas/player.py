from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime

class PlayerBase(BaseModel):
    number: int
    firstname: str
    lastname: str
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    homecontact: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    joindate: Optional[date] = None
    status: str = "active"
    organization_id: Optional[int] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['M', 'F']:
            raise ValueError('Gender must be M or F')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['active', 'inactive', 'suspended']:
            raise ValueError('Status must be active, inactive, or suspended')
        return v

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    homecontact: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    status: Optional[str] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['M', 'F']:
            raise ValueError('Gender must be M or F')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['active', 'inactive', 'suspended']:
            raise ValueError('Status must be active, inactive, or suspended')
        return v

class PlayerResponse(PlayerBase):
    id: int
    legacy_id: Optional[int] = None
    bmid: Optional[int] = None
    wbf_id: Optional[str] = None
    national_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    type: str
    parent_id: Optional[int] = None
    country: Optional[str] = None
    settings: Optional[dict] = {}
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['club', 'region', 'national', 'international']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
from typing import Optional
from pydantic import BaseModel, validator
from datetime import date, datetime

class EventBase(BaseModel):
    name: str
    type: str
    start_date: date
    end_date: Optional[date] = None
    organization_id: Optional[int] = None
    parent_event_id: Optional[int] = None
    code: Optional[str] = None
    status: str = "planned"
    settings: Optional[dict] = {}
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['pairs', 'teams', 'swiss', 'knockout', 'round_robin', 'bam']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['planned', 'active', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    code: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[dict] = None
    
    @validator('type')
    def validate_type(cls, v):
        if v:
            valid_types = ['pairs', 'teams', 'swiss', 'knockout', 'round_robin', 'bam']
            if v not in valid_types:
                raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v:
            valid_statuses = ['planned', 'active', 'completed', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class EventResponse(EventBase):
    id: int
    legacy_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
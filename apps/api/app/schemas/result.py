from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ResultBase(BaseModel):
    event_id: int
    player_id: int
    partner_id: Optional[int] = None
    session_id: Optional[int] = None
    pair_number: Optional[int] = None
    position: Optional[int] = None
    score: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    imp_score: Optional[Decimal] = None
    vp_score: Optional[Decimal] = None
    masterpoints_awarded: Optional[Decimal] = None

class ResultCreate(ResultBase):
    pass

class ResultResponse(ResultBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
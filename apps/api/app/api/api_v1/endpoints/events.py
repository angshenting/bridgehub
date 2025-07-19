from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db.session import get_db
from app.models.event import Event
from app.schemas.event import EventResponse, EventCreate, EventUpdate

router = APIRouter()

@router.get("/", response_model=List[EventResponse])
def get_events(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    organization_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None)
):
    """Get list of events with optional filtering"""
    query = db.query(Event)
    
    if status:
        query = query.filter(Event.status == status)
    if event_type:
        query = query.filter(Event.type == event_type)
    if organization_id:
        query = query.filter(Event.organization_id == organization_id)
    if from_date:
        query = query.filter(Event.start_date >= from_date)
    if to_date:
        query = query.filter(Event.start_date <= to_date)
    
    events = query.order_by(Event.start_date.desc()).offset(skip).limit(limit).all()
    return events

@router.get("/recent", response_model=List[EventResponse])
def get_recent_events(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get recent events within specified days"""
    cutoff_date = date.today() - timedelta(days=days)
    events = db.query(Event).filter(
        Event.start_date >= cutoff_date
    ).order_by(Event.start_date.desc()).limit(50).all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/{event_id}/results")
def get_event_results(event_id: int, db: Session = Depends(get_db)):
    """Get results for an event"""
    from app.models.result import Result
    from app.models.player import Player
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    results = db.query(Result, Player).join(
        Player, Result.player_id == Player.id
    ).filter(Result.event_id == event_id).order_by(Result.position).all()
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "results": [
            {
                "position": result.Result.position,
                "player_name": f"{result.Player.firstname} {result.Player.lastname}",
                "player_number": result.Player.number,
                "score": float(result.Result.score or 0),
                "percentage": float(result.Result.percentage or 0),
                "masterpoints": float(result.Result.masterpoints_awarded or 0)
            }
            for result in results
        ]
    }

@router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create new event"""
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Update event"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event
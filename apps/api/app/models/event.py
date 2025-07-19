from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    parent_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    legacy_id = Column(Integer, nullable=True, index=True)  # For migration
    code = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # pairs, teams, swiss, knockout, etc.
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="planned", index=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="events")
    parent_event = relationship("Event", remote_side=[id], back_populates="child_events")
    child_events = relationship("Event", back_populates="parent_event")
    sessions = relationship("Session", back_populates="event")
    results = relationship("Result", back_populates="event")
    ratings = relationship("Rating", back_populates="event")
    masterpoints = relationship("Masterpoint", back_populates="event")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    session_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="planned")
    boards_played = Column(Integer, nullable=True)
    movement_type = Column(String(50), nullable=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="sessions")
    results = relationship("Result", back_populates="session")
    hands = relationship("Hand", back_populates="session")
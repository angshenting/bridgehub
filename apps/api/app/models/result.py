from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("players.id"), nullable=True, index=True)
    pair_number = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True, index=True)
    score = Column(DECIMAL(10, 2), nullable=True)
    percentage = Column(DECIMAL(5, 2), nullable=True)
    imp_score = Column(DECIMAL(8, 2), nullable=True)
    vp_score = Column(DECIMAL(6, 2), nullable=True)
    masterpoints_awarded = Column(DECIMAL(6, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="results")
    event = relationship("Event", back_populates="results")
    player = relationship("Player", foreign_keys=[player_id], back_populates="results")
    partner = relationship("Player", foreign_keys=[partner_id], back_populates="partner_results")
    contracts = relationship("Contract", back_populates="result")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    rating_type = Column(String(20), nullable=False, index=True)  # openskill, elo, ngs
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    mu = Column(DECIMAL(8, 4), nullable=False)
    sigma = Column(DECIMAL(8, 4), nullable=False)
    mu_delta = Column(DECIMAL(8, 4), nullable=True)
    sigma_delta = Column(DECIMAL(8, 4), nullable=True)
    days_since_last = Column(Integer, nullable=True)
    confidence_interval = Column(DECIMAL(8, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="ratings")
    event = relationship("Event", back_populates="ratings")

class Masterpoint(Base):
    __tablename__ = "masterpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    award_type = Column(String(50), nullable=False, index=True)  # local, national, regional, international
    points = Column(DECIMAL(6, 2), nullable=False)
    level = Column(String(50), nullable=True)
    awarded_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="masterpoints")
    event = relationship("Event", back_populates="masterpoints")
    organization = relationship("Organization")
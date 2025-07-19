from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, CHAR, JSON, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    legacy_id = Column(Integer, nullable=True, index=True)  # For migration
    bmid = Column(Integer, unique=True, nullable=True)  # Bridgemate ID
    number = Column(Integer, nullable=False, unique=True, index=True)
    wbf_id = Column(String(20), nullable=True)
    national_id = Column(String(20), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    lastname = Column(String(255), nullable=False)
    firstname = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    mobile = Column(String(50), nullable=True)
    homecontact = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    gender = Column(CHAR(1), nullable=True)
    birthdate = Column(Date, nullable=True)
    joindate = Column(Date, nullable=True)
    status = Column(String(20), default="active", index=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="players")
    results = relationship("Result", foreign_keys="[Result.player_id]", back_populates="player")
    partner_results = relationship("Result", foreign_keys="[Result.partner_id]", back_populates="partner")
    ratings = relationship("Rating", back_populates="player")
    masterpoints = relationship("Masterpoint", back_populates="player")
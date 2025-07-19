from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Hand(Base):
    __tablename__ = "hands"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    board_number = Column(Integer, nullable=False, index=True)
    dealer = Column(String(5), nullable=False)  # N, S, E, W
    vulnerability = Column(String(10), nullable=False)  # None, NS, EW, All
    pbn_data = Column(Text, nullable=True)  # Portable Bridge Notation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="hands")
    contracts = relationship("Contract", back_populates="hand")

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("results.id"))
    hand_id = Column(Integer, ForeignKey("hands.id"))
    level = Column(Integer, nullable=False)  # 1-7
    suit = Column(String(10), nullable=False)  # C, D, H, S, NT
    doubled = Column(String(10), nullable=True)  # '', X, XX
    declarer = Column(String(5), nullable=False)  # N, S, E, W
    tricks = Column(Integer, nullable=False)  # 0-13
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    result = relationship("Result", back_populates="contracts")
    hand = relationship("Hand", back_populates="contracts")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    type = Column(String(50), nullable=False)  # full, social, student, life
    expiry = Column(DateTime, nullable=False, index=True)
    fee = Column(Integer, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    receipt = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="subscriptions")
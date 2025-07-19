from typing import Generator
from app.db.base import SessionLocal

def get_db() -> Generator:
    """Database dependency"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
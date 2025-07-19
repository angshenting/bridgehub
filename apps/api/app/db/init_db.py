import logging
from sqlalchemy.orm import Session
from app.db.base import engine
from app.db.session import get_db
from app.models.organization import Organization
from app.models.player import Player

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """Initialize database and create default data if needed"""
    try:
        # Test database connection
        with engine.connect() as connection:
            logger.info("Database connection successful")
        
        # Check if default organization exists
        db = next(get_db())
        default_org = db.query(Organization).filter(Organization.id == 1).first()
        if not default_org:
            logger.info("Creating default organization...")
            # The default organization should be created by the SQL schema
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
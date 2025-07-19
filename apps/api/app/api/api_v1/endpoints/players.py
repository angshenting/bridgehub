from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.player import Player
from app.schemas.player import PlayerResponse, PlayerCreate, PlayerUpdate

router = APIRouter()

@router.get("/", response_model=List[PlayerResponse])
def get_players(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    organization_id: Optional[int] = Query(None)
):
    """Get list of players with optional filtering"""
    query = db.query(Player)
    
    if status:
        query = query.filter(Player.status == status)
    if organization_id:
        query = query.filter(Player.organization_id == organization_id)
    
    players = query.offset(skip).limit(limit).all()
    return players

@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player by ID"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/masterpoints")
def get_player_masterpoints(player_id: int, db: Session = Depends(get_db)):
    """Get player's masterpoints summary"""
    from app.models.result import Masterpoint
    from sqlalchemy import func, case
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Calculate masterpoints by type
    masterpoints = db.query(
        func.sum(case((Masterpoint.award_type == 'local', Masterpoint.points), else_=0)).label('local_points'),
        func.sum(case((Masterpoint.award_type == 'national', Masterpoint.points), else_=0)).label('national_points'),
        func.sum(case((Masterpoint.award_type == 'regional', Masterpoint.points), else_=0)).label('regional_points'),
        func.sum(case((Masterpoint.award_type == 'international', Masterpoint.points), else_=0)).label('international_points'),
        func.sum(Masterpoint.points).label('total_points'),
        func.count(Masterpoint.id).label('events_played'),
        func.max(Masterpoint.awarded_date).label('last_award_date')
    ).filter(Masterpoint.player_id == player_id).first()
    
    return {
        "player_id": player_id,
        "local_points": float(masterpoints.local_points or 0),
        "national_points": float(masterpoints.national_points or 0),
        "regional_points": float(masterpoints.regional_points or 0),
        "international_points": float(masterpoints.international_points or 0),
        "total_points": float(masterpoints.total_points or 0),
        "events_played": masterpoints.events_played or 0,
        "last_award_date": masterpoints.last_award_date
    }

@router.get("/{player_id}/ratings")
def get_player_ratings(player_id: int, db: Session = Depends(get_db)):
    """Get player's current ratings"""
    from app.models.result import Rating
    from sqlalchemy import func
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Get latest rating for each type
    subquery = db.query(
        Rating.rating_type,
        func.max(Rating.date).label('max_date')
    ).filter(Rating.player_id == player_id).group_by(Rating.rating_type).subquery()
    
    ratings = db.query(Rating).join(
        subquery,
        (Rating.rating_type == subquery.c.rating_type) &
        (Rating.date == subquery.c.max_date)
    ).filter(Rating.player_id == player_id).all()
    
    return {
        "player_id": player_id,
        "ratings": [
            {
                "type": rating.rating_type,
                "mu": float(rating.mu),
                "sigma": float(rating.sigma),
                "conservative_rating": float(rating.mu - 2 * rating.sigma),
                "date": rating.date
            }
            for rating in ratings
        ]
    }

@router.post("/", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Create new player"""
    # Check if player number already exists
    existing = db.query(Player).filter(Player.number == player.number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Player number already exists")
    
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, player_update: PlayerUpdate, db: Session = Depends(get_db)):
    """Update player"""
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    update_data = player_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_player, field, value)
    
    db.commit()
    db.refresh(db_player)
    return db_player
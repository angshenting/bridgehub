from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.result import Result
from app.schemas.result import ResultResponse, ResultCreate

router = APIRouter()

@router.get("/event/{event_id}", response_model=List[ResultResponse])
def get_event_results(
    event_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000)
):
    """Get results for a specific event"""
    results = db.query(Result).filter(
        Result.event_id == event_id
    ).order_by(Result.position).offset(skip).limit(limit).all()
    return results

@router.get("/player/{player_id}", response_model=List[ResultResponse])
def get_player_results(
    player_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get results for a specific player"""
    results = db.query(Result).filter(
        Result.player_id == player_id
    ).order_by(Result.created_at.desc()).offset(skip).limit(limit).all()
    return results

@router.post("/", response_model=ResultResponse)
def create_result(result: ResultCreate, db: Session = Depends(get_db)):
    """Create new result"""
    db_result = Result(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/leaderboard")
def get_leaderboard(
    db: Session = Depends(get_db),
    period: str = Query("all", regex="^(week|month|year|all)$"),
    limit: int = Query(50, ge=1, le=100)
):
    """Get masterpoints leaderboard"""
    from app.models.result import Masterpoint
    from app.models.player import Player
    from sqlalchemy import func, and_
    from datetime import date, timedelta
    
    query = db.query(
        Player.id,
        Player.firstname,
        Player.lastname,
        Player.number,
        func.sum(Masterpoint.points).label('total_points'),
        func.count(Masterpoint.id).label('events_played')
    ).join(Masterpoint, Player.id == Masterpoint.player_id)
    
    # Apply date filter based on period
    if period != "all":
        if period == "week":
            cutoff_date = date.today() - timedelta(days=7)
        elif period == "month":
            cutoff_date = date.today() - timedelta(days=30)
        elif period == "year":
            cutoff_date = date.today() - timedelta(days=365)
        
        query = query.filter(Masterpoint.awarded_date >= cutoff_date)
    
    leaderboard = query.group_by(
        Player.id, Player.firstname, Player.lastname, Player.number
    ).order_by(func.sum(Masterpoint.points).desc()).limit(limit).all()
    
    return {
        "period": period,
        "leaderboard": [
            {
                "rank": idx + 1,
                "player_id": player.id,
                "player_name": f"{player.firstname} {player.lastname}",
                "player_number": player.number,
                "total_points": float(player.total_points),
                "events_played": player.events_played
            }
            for idx, player in enumerate(leaderboard)
        ]
    }
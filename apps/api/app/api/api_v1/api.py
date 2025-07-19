from fastapi import APIRouter
from app.api.api_v1.endpoints import players, events, results, organizations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
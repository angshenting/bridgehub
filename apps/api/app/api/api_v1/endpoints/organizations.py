from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationCreate

router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    """Get list of all organizations"""
    organizations = db.query(Organization).all()
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    """Get organization by ID"""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.post("/", response_model=OrganizationResponse)
def create_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    """Create new organization"""
    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization
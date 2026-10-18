from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/me")
async def get_my_profile(db: AsyncSession = Depends(get_db)):
    """Get current donor's profile."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/me")
async def update_profile(db: AsyncSession = Depends(get_db)):
    """Update donor profile (availability, location, preferred hours)."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/me/availability")
async def toggle_availability(db: AsyncSession = Depends(get_db)):
    """Quick toggle donor availability on/off."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/nearby")
async def find_nearby_donors(
    blood_group: str,
    lat: float,
    lng: float,
    radius_km: float = 15.0,
    db: AsyncSession = Depends(get_db),
):
    """Search for nearby available donors by blood group and location."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/me/history")
async def donation_history(db: AsyncSession = Depends(get_db)):
    """Get donor's past donation responses."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

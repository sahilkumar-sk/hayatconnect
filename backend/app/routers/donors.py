from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User, BloodGroup

router = APIRouter()


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current donor's profile."""
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "phone": current_user.phone,
        "email": current_user.email,
        "role": current_user.role.value,
        "blood_group": current_user.blood_group.value if current_user.blood_group else None,
        "area": current_user.area,
        "latitude": current_user.latitude,
        "longitude": current_user.longitude,
        "is_available": current_user.is_available,
        "preferred_hours_start": current_user.preferred_hours_start,
        "preferred_hours_end": current_user.preferred_hours_end,
        "reliability_score": current_user.reliability_score,
        "is_phone_verified": current_user.is_phone_verified,
        "last_donation_date": current_user.last_donation_date,
        "created_at": current_user.created_at,
    }


@router.patch("/me")
async def update_profile(
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update donor profile (availability, location, preferred hours)."""
    allowed_fields = {
        "name", "area", "latitude", "longitude", "blood_group",
        "is_available", "preferred_hours_start", "preferred_hours_end",
    }

    for key, value in updates.items():
        if key not in allowed_fields:
            continue
        if key == "blood_group" and value:
            value = BloodGroup(value)
        setattr(current_user, key, value)

    return {"message": "Profile updated"}


@router.patch("/me/availability")
async def toggle_availability(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Quick toggle donor availability on/off."""
    current_user.is_available = not current_user.is_available
    return {"is_available": current_user.is_available}


@router.get("/nearby")
async def find_nearby_donors(
    blood_group: str,
    lat: float,
    lng: float,
    radius_km: float = 15.0,
    db: AsyncSession = Depends(get_db),
):
    """Search for nearby available donors by blood group and location."""
    # TODO: Week 4 — Haversine distance filtering
    result = await db.execute(
        select(User).where(
            User.blood_group == BloodGroup(blood_group),
            User.is_available == True,  # noqa: E712
        )
    )
    donors = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "name": d.name,
            "area": d.area,
            "blood_group": d.blood_group.value if d.blood_group else None,
            "reliability_score": d.reliability_score,
        }
        for d in donors
    ]


@router.get("/me/history")
async def donation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get donor's past donation responses."""
    # TODO: Week 3 — join with donor_responses and blood_requests
    return []
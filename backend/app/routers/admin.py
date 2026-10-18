from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/flags")
async def list_fraud_flags(status_filter: str | None = None, db: AsyncSession = Depends(get_db)):
    """List fraud flags for admin review."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/flags/{flag_id}")
async def update_flag(flag_id: str, new_status: str, db: AsyncSession = Depends(get_db)):
    """Update fraud flag status (reviewed, dismissed, actioned)."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/stats")
async def platform_stats(db: AsyncSession = Depends(get_db)):
    """Get platform-wide statistics dashboard data."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/users/{user_id}/ban")
async def ban_user(user_id: str, reason: str, db: AsyncSession = Depends(get_db)):
    """Ban a user from the platform."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

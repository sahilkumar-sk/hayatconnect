from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.post("/{request_id}/match")
async def trigger_matching(request_id: str, db: AsyncSession = Depends(get_db)):
    """Run AI matching algorithm to find and rank eligible donors."""
    # TODO: Week 4 — Haversine + weighted scoring + notification
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{request_id}/respond")
async def donor_respond(
    request_id: str,
    action: str,  # accept / decline / snooze
    db: AsyncSession = Depends(get_db),
):
    """Donor responds to a match notification."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{response_id}/complete")
async def mark_completed(response_id: str, db: AsyncSession = Depends(get_db)):
    """Mark a donation as completed (both sides confirm)."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{response_id}/rate")
async def rate_donation(response_id: str, score: int, comment: str = "", db: AsyncSession = Depends(get_db)):
    """Rate a completed donation (1-5 stars)."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut

router = APIRouter()


@router.post("/", response_model=BloodRequestOut, status_code=status.HTTP_201_CREATED)
async def create_request(payload: BloodRequestCreate, db: AsyncSession = Depends(get_db)):
    """Create a new blood request."""
    # TODO: Week 3 — create request, auto-set expiry, trigger matching
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/")
async def list_requests(
    status_filter: str | None = None,
    blood_group: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List blood requests with optional filters."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{request_id}", response_model=BloodRequestOut)
async def get_request(request_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific blood request with donor responses."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/{request_id}/cancel")
async def cancel_request(request_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel an open blood request."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

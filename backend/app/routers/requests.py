from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.blood_request import BloodRequest, BloodGroup, UrgencyLevel, RequestStatus
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut
from app.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/", response_model=BloodRequestOut, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: BloodRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new blood request."""
    # Set expiry based on urgency
    expiry_hours = {
        "emergency": 24,
        "urgent": 48,
        "routine": 72,
    }
    hours = expiry_hours.get(payload.urgency, settings.REQUEST_EXPIRY_HOURS)

    request = BloodRequest(
        requester_id=current_user.id,
        patient_name=payload.patient_name,
        blood_group_needed=BloodGroup(payload.blood_group_needed),
        units_needed=payload.units_needed,
        hospital_name=payload.hospital_name,
        hospital_address=payload.hospital_address,
        hospital_latitude=payload.hospital_latitude,
        hospital_longitude=payload.hospital_longitude,
        urgency=UrgencyLevel(payload.urgency),
        notes=payload.notes,
        contact_phone=payload.contact_phone or current_user.phone,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
    )

    db.add(request)
    await db.flush()

    return request


@router.get("/")
async def list_requests(
    status_filter: str | None = Query(None, alias="status"),
    blood_group: str | None = None,
    urgency: str | None = None,
    requester_id: UUID | None = None,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List blood requests with optional filters. Public endpoint."""
    query = select(BloodRequest).order_by(BloodRequest.created_at.desc())

    if status_filter:
        query = query.where(BloodRequest.status == RequestStatus(status_filter))
    else:
        # Default: show only open/partially fulfilled (not expired/cancelled)
        query = query.where(
            BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.PARTIALLY_FULFILLED])
        )

    if blood_group:
        query = query.where(BloodRequest.blood_group_needed == BloodGroup(blood_group))

    if urgency:
        query = query.where(BloodRequest.urgency == UrgencyLevel(urgency))

    query = query.offset(offset).limit(limit)
    if requester_id:
        query = query.where(BloodRequest.requester_id == requester_id)
    result = await db.execute(query)
    requests = result.scalars().all()

    # Auto-expire old requests
    now = datetime.now(timezone.utc)
    for req in requests:
        if req.status == RequestStatus.OPEN and req.expires_at < now:
            req.status = RequestStatus.EXPIRED

    return [
        {
            "id": str(r.id),
            "requester_id": str(r.requester_id),
            "patient_name": r.patient_name,
            "blood_group_needed": r.blood_group_needed.value,
            "units_needed": r.units_needed,
            "units_fulfilled": r.units_fulfilled,
            "hospital_name": r.hospital_name,
            "hospital_address": r.hospital_address,
            "urgency": r.urgency.value,
            "status": r.status.value,
            "expires_at": r.expires_at.isoformat(),
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]


@router.get("/{request_id}")
async def get_request(request_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific blood request with details."""
    result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == UUID(request_id))
    )
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Auto-expire check
    now = datetime.now(timezone.utc)
    if req.status == RequestStatus.OPEN and req.expires_at < now:
        req.status = RequestStatus.EXPIRED

    return {
        "id": str(req.id),
        "requester_id": str(req.requester_id),
        "patient_name": req.patient_name,
        "blood_group_needed": req.blood_group_needed.value,
        "units_needed": req.units_needed,
        "units_fulfilled": req.units_fulfilled,
        "hospital_name": req.hospital_name,
        "hospital_address": req.hospital_address,
        "hospital_latitude": req.hospital_latitude,
        "hospital_longitude": req.hospital_longitude,
        "urgency": req.urgency.value,
        "status": req.status.value,
        "notes": req.notes,
        "contact_phone": req.contact_phone,
        "expires_at": req.expires_at.isoformat(),
        "created_at": req.created_at.isoformat(),
    }


@router.patch("/{request_id}/cancel")
async def cancel_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an open blood request. Only the requester can cancel."""
    result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == UUID(request_id))
    )
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own requests")

    if req.status not in (RequestStatus.OPEN, RequestStatus.PARTIALLY_FULFILLED):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {req.status.value} request")

    req.status = RequestStatus.CANCELLED
    return {"message": "Request cancelled", "status": "cancelled"}
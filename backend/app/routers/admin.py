from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.blood_request import BloodRequest
from app.models.donor_response import DonorResponse

router = APIRouter()


def _v(x):
    """Enum member -> its stored value."""
    return getattr(x, "value", x)


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if _v(current_user.role) != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/flags")
async def list_fraud_flags(
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List fraud flags for admin review."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/flags/{flag_id}")
async def update_flag(
    flag_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update fraud flag status (reviewed, dismissed, actioned)."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Platform-wide statistics for the admin dashboard."""

    async def grouped(col, model):
        rows = await db.execute(select(col, func.count()).select_from(model).group_by(col))
        return {str(_v(k)): n for k, n in rows.all()}

    users_by_role = await grouped(User.role, User)
    requests_by_status = await grouped(BloodRequest.status, BloodRequest)
    requests_by_urgency = await grouped(BloodRequest.urgency, BloodRequest)
    requests_by_group = await grouped(BloodRequest.blood_group_needed, BloodRequest)
    responses_by_status = await grouped(DonorResponse.status, DonorResponse)

    total_users = sum(users_by_role.values())
    total_requests = sum(requests_by_status.values())

    available_donors = (
        await db.execute(
            select(func.count()).select_from(User).where(
                User.is_available.is_(True), User.blood_group.is_not(None)
            )
        )
    ).scalar_one()

    units = (
        await db.execute(
            select(
                func.coalesce(func.sum(BloodRequest.units_needed), 0),
                func.coalesce(func.sum(BloodRequest.units_fulfilled), 0),
            )
        )
    ).one()
    units_needed, units_fulfilled = int(units[0]), int(units[1])

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    requests_7d = (
        await db.execute(
            select(func.count()).select_from(BloodRequest).where(BloodRequest.created_at >= week_ago)
        )
    ).scalar_one()

    responded = sum(n for s, n in responses_by_status.items() if s != "notified")
    positive = responses_by_status.get("accepted", 0) + responses_by_status.get("completed", 0)

    recent_rows = await db.execute(
        select(BloodRequest).order_by(BloodRequest.created_at.desc()).limit(10)
    )
    recent = [
        {
            "id": str(r.id),
            "blood_group": str(_v(r.blood_group_needed)),
            "hospital_name": r.hospital_name,
            "urgency": str(_v(r.urgency)),
            "status": str(_v(r.status)),
            "units_needed": r.units_needed,
            "units_fulfilled": r.units_fulfilled,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_rows.scalars().all()
    ]

    return {
        "total_users": total_users,
        "users_by_role": users_by_role,
        "available_donors": available_donors,
        "total_requests": total_requests,
        "requests_last_7_days": requests_7d,
        "requests_by_status": requests_by_status,
        "requests_by_urgency": requests_by_urgency,
        "requests_by_blood_group": requests_by_group,
        "units_needed": units_needed,
        "units_fulfilled": units_fulfilled,
        "fulfilment_rate": round(units_fulfilled / units_needed * 100, 1) if units_needed else 0,
        "responses_by_status": responses_by_status,
        "acceptance_rate": round(positive / responded * 100, 1) if responded else 0,
        "recent_requests": recent,
    }


@router.get("/users")
async def list_users(
    search: str | None = None,
    role: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List users with optional search (name, phone, email) and role filter."""
    if role and role not in ("donor", "requester", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    query = select(User).order_by(User.created_at.desc())
    if search:
        like = f"%{search}%"
        query = query.where(
            or_(User.name.ilike(like), User.phone.ilike(like), User.email.ilike(like))
        )
    if role:
        query = query.where(User.role == role)

    rows = await db.execute(query.offset(offset).limit(min(limit, 200)))
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "phone": u.phone,
            "email": u.email,
            "role": str(_v(u.role)),
            "blood_group": str(_v(u.blood_group)) if u.blood_group else None,
            "area": u.area,
            "is_available": u.is_available,
            "is_phone_verified": u.is_phone_verified,
            "is_active": u.is_active,
            "ban_reason": u.ban_reason,
            "reliability_score": u.reliability_score,
            "last_donation_date": u.last_donation_date.isoformat() if u.last_donation_date else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in rows.scalars().all()
    ]


@router.patch("/users/{user_id}/verify")
async def toggle_verified(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Toggle the verified badge on a user."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_phone_verified = not user.is_phone_verified
    await db.commit()
    return {"id": str(user.id), "is_phone_verified": user.is_phone_verified}

async def _get_target(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Suspend a user: they cannot log in and are skipped by matching."""
    user = await _get_target(db, user_id)
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot ban yourself")
    if _v(user.role) == "admin":
        raise HTTPException(status_code=400, detail="Admins cannot be banned")
    user.is_active = False
    user.is_available = False
    user.ban_reason = reason.strip()[:255] or "No reason given"
    await db.commit()
    return {"id": str(user.id), "is_active": False, "ban_reason": user.ban_reason}


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Lift a suspension. The donor turns availability back on themselves."""
    user = await _get_target(db, user_id)
    user.is_active = True
    user.ban_reason = None
    await db.commit()
    return {"id": str(user.id), "is_active": True, "ban_reason": None}

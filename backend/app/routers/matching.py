from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.blood_request import BloodRequest, RequestStatus
from app.models.donor_response import DonorResponse, ResponseStatus
from app.models.rating import Rating
from app.services.matching_service import find_matching_donors, haversine_km
from app.services.notifications import notify_donor_new_request

router = APIRouter()


@router.post("/{request_id}/match")
async def trigger_matching(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run AI matching algorithm to find and rank eligible donors."""
    result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == UUID(request_id))
    )
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only match your own requests")

    if req.status not in (RequestStatus.OPEN, RequestStatus.PARTIALLY_FULFILLED):
        raise HTTPException(status_code=400, detail=f"Cannot match a {req.status.value} request")

    # Run the matching algorithm (only finds donors not yet notified)
    matches = await find_matching_donors(req, db)

    for match in matches:
        db.add(DonorResponse(
            request_id=req.id,
            donor_id=match["donor"].id,
            status=ResponseStatus.NOTIFIED,
            rank_score=match["score"],
        ))
    await db.flush()

    # SMS each newly matched donor (console in dev, Twilio in prod)
    for match in matches:
        d = match["donor"]
        await notify_donor_new_request(
            d.phone,
            d.name,
            getattr(req.blood_group_needed, "value", str(req.blood_group_needed)),
            req.hospital_name,
            getattr(req.urgency, "value", str(req.urgency)),
        )
    # Return every donor matched to this request, new and previous
    rows = await db.execute(
        select(DonorResponse, User)
        .join(User, User.id == DonorResponse.donor_id)
        .where(DonorResponse.request_id == req.id)
        .order_by(DonorResponse.rank_score.desc())
    )
    donors = []
    for resp, donor in rows.all():
        dist = None
        if donor.latitude is not None and req.hospital_latitude is not None:
            dist = round(haversine_km(donor.latitude, donor.longitude,
                                      req.hospital_latitude, req.hospital_longitude), 1)
        donors.append({
            "donor_id": str(donor.id),
            "donor_name": donor.name,
            "blood_group": donor.blood_group.value if donor.blood_group else None,
            "distance_km": dist,
            "score": resp.rank_score,
            "area": donor.area,
            "status": resp.status.value,
        })

    return {
        "message": f"{len(donors)} donor(s) matched",
        "matched_count": len(donors),
        "donors": donors,
    }

@router.get("/inbox")
async def donor_inbox(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Requests this donor has been matched to, newest first."""
    rows = await db.execute(
        select(DonorResponse, BloodRequest)
        .join(BloodRequest, BloodRequest.id == DonorResponse.request_id)
        .where(DonorResponse.donor_id == current_user.id)
        .order_by(BloodRequest.created_at.desc())
    )
    return [
        {
            "response_id": str(resp.id),
            "request_id": str(req.id),
            "status": resp.status.value,
            "rank_score": resp.rank_score,
            "blood_group_needed": req.blood_group_needed.value,
            "hospital_name": req.hospital_name,
            "urgency": req.urgency.value,
            "units_needed": req.units_needed,
            "units_fulfilled": req.units_fulfilled,
            "request_status": req.status.value,
            "expires_at": req.expires_at.isoformat(),
        }
        for resp, req in rows.all()
    ]

@router.get("/{request_id}/contacts")
async def request_contacts(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reveal phone numbers only after a donor has accepted."""
    result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == UUID(request_id))
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    accepted = [ResponseStatus.ACCEPTED, ResponseStatus.COMPLETED]

    # Requester sees every donor who accepted
    if req.requester_id == current_user.id:
        rows = await db.execute(
            select(DonorResponse, User)
            .join(User, User.id == DonorResponse.donor_id)
            .where(DonorResponse.request_id == req.id, DonorResponse.status.in_(accepted))
        )
        return {
            "role": "requester",
            "contacts": [
                {"name": u.name, "phone": u.phone, "status": r.status.value}
                for r, u in rows.all()
            ],
        }

    # A donor sees the requester's contact only if they accepted
    mine = await db.execute(
        select(DonorResponse).where(
            DonorResponse.request_id == req.id,
            DonorResponse.donor_id == current_user.id,
            DonorResponse.status.in_(accepted),
        )
    )
    if not mine.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Accept the request to see contact details")

    requester = await db.get(User, req.requester_id)
    return {
        "role": "donor",
        "contacts": [
            {"name": requester.name, "phone": req.contact_phone or requester.phone, "status": "requester"}
        ],
    }

@router.post("/{request_id}/respond")
async def donor_respond(
    request_id: str,
    action: str,  # accept | decline | snooze
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Donor responds to a match notification."""
    if action not in ("accept", "decline", "snooze"):
        raise HTTPException(status_code=400, detail="Action must be accept, decline, or snooze")

    # Find the donor's response entry for this request
    result = await db.execute(
        select(DonorResponse).where(
            DonorResponse.request_id == UUID(request_id),
            DonorResponse.donor_id == current_user.id,
        )
    )
    response = result.scalar_one_or_none()

    if not response:
        raise HTTPException(status_code=404, detail="No match found for you on this request")

    if response.status != ResponseStatus.NOTIFIED:
        raise HTTPException(
            status_code=400,
            detail=f"Already responded with: {response.status.value}",
        )

    status_map = {
        "accept": ResponseStatus.ACCEPTED,
        "decline": ResponseStatus.DECLINED,
        "snooze": ResponseStatus.SNOOZED,
    }

    response.status = status_map[action]
    response.responded_at = datetime.now(timezone.utc)

    # If accepted, update the blood request's fulfilled count
    if action == "accept":
        req_result = await db.execute(
            select(BloodRequest).where(BloodRequest.id == UUID(request_id))
        )
        req = req_result.scalar_one_or_none()
        if req:
            req.units_fulfilled += 1
            if req.units_fulfilled >= req.units_needed:
                req.status = RequestStatus.FULFILLED
            else:
                req.status = RequestStatus.PARTIALLY_FULFILLED

    # Update reliability score on decline/no-show
    if action == "decline":
        # Small penalty for declining (but it's their right)
        current_user.reliability_score = max(0, current_user.reliability_score - 1)

    return {
        "message": f"Response recorded: {action}",
        "status": response.status.value,
    }


@router.post("/{response_id}/complete")
async def mark_completed(
    response_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a donation as completed (requester confirms)."""
    result = await db.execute(
        select(DonorResponse).where(DonorResponse.id == UUID(response_id))
    )
    response = result.scalar_one_or_none()

    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    if response.status != ResponseStatus.ACCEPTED:
        raise HTTPException(
            status_code=400,
            detail="Can only complete an accepted donation",
        )

    # Verify the requester owns the blood request
    req_result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == response.request_id)
    )
    req = req_result.scalar_one_or_none()

    if not req or req.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the requester can confirm completion")

    response.status = ResponseStatus.COMPLETED
    response.completed_at = datetime.now(timezone.utc)

    # Update donor's last donation date and reliability
    donor_result = await db.execute(
        select(User).where(User.id == response.donor_id)
    )
    donor = donor_result.scalar_one_or_none()
    if donor:
        donor.last_donation_date = datetime.now(timezone.utc)
        donor.reliability_score = min(100, donor.reliability_score + 5)

    return {"message": "Donation marked as completed", "status": "completed"}


@router.post("/{response_id}/rate")
async def rate_donation(
    response_id: str,
    score: int,
    comment: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rate a completed donation (1-5 stars)."""
    if score < 1 or score > 5:
        raise HTTPException(status_code=400, detail="Score must be 1-5")

    result = await db.execute(
        select(DonorResponse).where(DonorResponse.id == UUID(response_id))
    )
    response = result.scalar_one_or_none()

    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    if response.status != ResponseStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only rate completed donations")

    # Check if already rated
    existing = await db.execute(
        select(Rating).where(
            Rating.response_id == response.id,
            Rating.rated_by == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already rated this donation")

    # Determine who is being rated
    # If current user is the requester â†’ rating the donor, and vice versa
    req_result = await db.execute(
        select(BloodRequest).where(BloodRequest.id == response.request_id)
    )
    req = req_result.scalar_one_or_none()

    if current_user.id == req.requester_id:
        rated_user_id = response.donor_id
    elif current_user.id == response.donor_id:
        rated_user_id = req.requester_id
    else:
        raise HTTPException(status_code=403, detail="Not involved in this donation")

    rating = Rating(
        response_id=response.id,
        rated_by=current_user.id,
        rated_user=rated_user_id,
        score=score,
        comment=comment,
    )
    db.add(rating)

    # Update the rated user's reliability based on rating
    rated_result = await db.execute(select(User).where(User.id == rated_user_id))
    rated_user = rated_result.scalar_one_or_none()
    if rated_user:
        # Adjust reliability: 3 is neutral, above adds, below subtracts
        adjustment = (score - 3) * 2
        rated_user.reliability_score = max(0, min(100, rated_user.reliability_score + adjustment))

    return {"message": "Rating submitted", "score": score}

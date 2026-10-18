"""
Donor Matching Algorithm for HayatConnect

Ranks eligible donors using a weighted scoring system:
  - Distance (Haversine):    30%   — closer donors rank higher
  - Eligibility recency:     20%   — last donation must be 90+ days ago
  - Reliability score:       25%   — based on past show-up rate
  - Availability window:     15%   — donor's preferred hours vs current time
  - Blood group match type:  10%   — exact match > compatible match

Total score: 0–100, higher is better.
"""

import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, BloodGroup
from app.models.blood_request import BloodRequest
from app.models.donor_response import DonorResponse, ResponseStatus
from app.config import get_settings

settings = get_settings()

# ── Blood group compatibility ─────────────────────────────────────
# Maps each needed blood group to compatible donor groups
BLOOD_COMPATIBILITY: dict[str, list[str]] = {
    "A+":  ["A+", "A-", "O+", "O-"],
    "A-":  ["A-", "O-"],
    "B+":  ["B+", "B-", "O+", "O-"],
    "B-":  ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],  # universal recipient
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+":  ["O+", "O-"],
    "O-":  ["O-"],  # universal donor only from O-
}

# Minimum days between donations
MIN_DONATION_GAP_DAYS = 90


# ── Haversine distance (km) ───────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ── Scoring functions ─────────────────────────────────────────────

def score_distance(distance_km: float, max_radius: float) -> float:
    """0–100: closer = higher score. Linear decay."""
    if distance_km >= max_radius:
        return 0.0
    return 100.0 * (1 - distance_km / max_radius)


def score_eligibility(last_donation_date: datetime | None) -> float:
    """0 or 100: eligible (90+ days since last donation) or not."""
    if last_donation_date is None:
        return 100.0  # Never donated — fully eligible
    days_since = (datetime.now(timezone.utc) - last_donation_date).days
    if days_since < MIN_DONATION_GAP_DAYS:
        return 0.0  # Ineligible
    # Bonus for longer gap (more recovered)
    return min(100.0, 50.0 + (days_since - MIN_DONATION_GAP_DAYS) * 0.5)


def score_reliability(reliability: float) -> float:
    """0–100: directly maps from the user's reliability_score."""
    return max(0.0, min(100.0, reliability))


def score_availability_window(
    preferred_start: int | None,
    preferred_end: int | None,
) -> float:
    """0–100: is the current hour within the donor's preferred hours?"""
    if preferred_start is None or preferred_end is None:
        return 75.0  # No preference set — assume mostly available

    current_hour = datetime.now(timezone.utc).hour  # TODO: convert to PKT (UTC+5)

    if preferred_start <= preferred_end:
        in_window = preferred_start <= current_hour < preferred_end
    else:
        # Wraps around midnight (e.g., 22–6)
        in_window = current_hour >= preferred_start or current_hour < preferred_end

    return 100.0 if in_window else 30.0


def score_blood_match(donor_group: str, needed_group: str) -> float:
    """100 for exact match, 70 for compatible, 0 for incompatible."""
    if donor_group == needed_group:
        return 100.0
    compatible = BLOOD_COMPATIBILITY.get(needed_group, [])
    if donor_group in compatible:
        return 70.0
    return 0.0


def calculate_donor_score(
    donor: User,
    hospital_lat: float,
    hospital_lng: float,
    needed_blood_group: str,
    max_radius: float,
) -> float | None:
    """
    Calculate a weighted donor ranking score (0–100).
    Returns None if the donor is ineligible (wrong blood group or too recent donation).
    """
    # Blood compatibility check — hard filter
    donor_bg = donor.blood_group.value if donor.blood_group else None
    if not donor_bg:
        return None

    blood_score = score_blood_match(donor_bg, needed_blood_group)
    if blood_score == 0.0:
        return None

    # Eligibility check — hard filter
    eligibility = score_eligibility(donor.last_donation_date)
    if eligibility == 0.0:
        return None

    # Distance check
    if donor.latitude is None or donor.longitude is None:
        return None

    distance = haversine_km(donor.latitude, donor.longitude, hospital_lat, hospital_lng)
    dist_score = score_distance(distance, max_radius)
    if dist_score == 0.0:
        return None

    # Availability window
    avail_score = score_availability_window(
        donor.preferred_hours_start, donor.preferred_hours_end
    )

    # Reliability
    rel_score = score_reliability(donor.reliability_score)

    # Weighted total
    total = (
        dist_score * 0.30
        + eligibility * 0.20
        + rel_score * 0.25
        + avail_score * 0.15
        + blood_score * 0.10
    )

    return round(total, 2)


# ── Main matching function ────────────────────────────────────────

async def find_matching_donors(
    request: BloodRequest,
    db: AsyncSession,
    max_donors: int | None = None,
    radius_km: float | None = None,
) -> list[dict]:
    """
    Find and rank eligible donors for a blood request.

    Returns a list of {donor, score, distance_km} dicts, sorted by score descending.
    """
    max_donors = max_donors or settings.MAX_DONORS_TO_NOTIFY
    radius = radius_km or settings.MATCH_RADIUS_KM

    if not request.hospital_latitude or not request.hospital_longitude:
        return []

    needed_bg = request.blood_group_needed.value
    compatible_groups = BLOOD_COMPATIBILITY.get(needed_bg, [needed_bg])

    # Fetch available donors with compatible blood groups
    bg_enums = [BloodGroup(bg) for bg in compatible_groups]
    result = await db.execute(
        select(User).where(
            User.role == "donor",
            User.is_available == True,  # noqa: E712
            User.blood_group.in_(bg_enums),
        )
    )
    candidates = result.scalars().all()

    # Score each candidate
    ranked = []
    for donor in candidates:
        # Skip if donor already responded to this request
        existing = await db.execute(
            select(DonorResponse).where(
                DonorResponse.request_id == request.id,
                DonorResponse.donor_id == donor.id,
            )
        )
        if existing.scalar_one_or_none():
            continue

        score = calculate_donor_score(
            donor,
            request.hospital_latitude,
            request.hospital_longitude,
            needed_bg,
            radius,
        )

        if score is not None:
            distance = haversine_km(
                donor.latitude, donor.longitude,
                request.hospital_latitude, request.hospital_longitude,
            )
            ranked.append({
                "donor": donor,
                "score": score,
                "distance_km": round(distance, 1),
            })

    # Sort by score descending, take top N
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:max_donors]
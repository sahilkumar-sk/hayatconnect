from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BloodRequestCreate(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=100)
    blood_group_needed: str
    units_needed: int = Field(default=1, ge=1, le=10)
    hospital_name: str = Field(..., max_length=200)
    hospital_address: str | None = None
    hospital_latitude: float | None = None
    hospital_longitude: float | None = None
    urgency: str = "urgent"  # routine | urgent | emergency
    notes: str | None = None
    contact_phone: str | None = None


class BloodRequestOut(BaseModel):
    id: UUID
    requester_id: UUID
    patient_name: str
    blood_group_needed: str
    units_needed: int
    units_fulfilled: int
    hospital_name: str
    urgency: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
